"""Basin-aware drainage routing and visible river-channel selection."""

from __future__ import annotations

import math
from collections import defaultdict

from rnr_mapgen.board import display_to_axial, iter_neighbor_coords
from rnr_mapgen.types import MapData


BASE_RUNOFF = 0.45
MOISTURE_RUNOFF_WEIGHT = 1.25
UPLAND_RUNOFF_WEIGHT = 1.00
COLD_RUNOFF_WEIGHT = 0.25
DOWNHILL_EPSILON = 1e-6
MIN_SOURCE_ELEVATION = 0.36
MIN_SOURCE_FLOW = 7.0
MOUTH_FLOW_QUANTILE = 0.86
TRIBUTARY_FLOW_QUANTILE = 0.74
MIN_TRIBUTARY_RATIO = 0.34
MAX_VISIBLE_RIVER_RATIO = 0.12
RIVER_STRENGTH_SCALE = 2.2


def generate_hydrology(map_data: MapData) -> MapData:
    """Populate deterministic drainage routing and visible river channels."""
    _reset_hydrology_fields(map_data)
    upstream_map = _assign_downstream_receivers(map_data)
    _accumulate_flow(map_data)
    _mark_visible_rivers(map_data, upstream_map)
    return map_data


def render_ascii_preview(map_data: MapData) -> str:
    """Render a compact ASCII preview using land, water, and river markers."""
    lines: list[str] = []

    for display_row in range(map_data.height):
        chars: list[str] = []
        for display_col in range(map_data.width):
            tile = map_data.tiles[display_to_axial(display_col, display_row)]
            if tile.is_water:
                chars.append(".")
            elif tile.has_river:
                chars.append("~")
            else:
                chars.append("#")

        indent = " " if display_row % 2 else ""
        lines.append(f"{indent}{''.join(chars)}")

    return "\n".join(lines)


def summarize_hydrology(map_data: MapData) -> str:
    """Return a concise terrain and river summary for CLI output."""
    elevation_values = [tile.elevation for tile in map_data.tiles.values()]
    moisture_values = [tile.moisture for tile in map_data.tiles.values()]
    temperature_values = [tile.temperature for tile in map_data.tiles.values()]
    land_tiles = sum(1 for tile in map_data.tiles.values() if not tile.is_water)
    water_tiles = map_data.tile_count - land_tiles
    river_tiles = sum(1 for tile in map_data.tiles.values() if tile.has_river)
    max_river_strength = max((tile.river_strength for tile in map_data.tiles.values()), default=0.0)
    land_percentage = (land_tiles / map_data.tile_count) * 100.0

    return "\n".join(
        [
            "RiftandReign first-pass hydrology groundwork.",
            f"Dimensions: {map_data.width}x{map_data.height}",
            f"Seed: {map_data.seed}",
            f"Total tiles: {map_data.tile_count}",
            f"Land tiles: {land_tiles}",
            f"Water tiles: {water_tiles}",
            f"Land percentage: {land_percentage:.1f}%",
            f"River tiles: {river_tiles}",
            f"Max river strength: {max_river_strength:.2f}",
            f"Elevation range: {min(elevation_values):.3f}..{max(elevation_values):.3f}",
            f"Moisture range: {min(moisture_values):.3f}..{max(moisture_values):.3f}",
            (
                "Temperature range: "
                f"{min(temperature_values):.3f}..{max(temperature_values):.3f}"
            ),
            "ASCII terrain preview:",
            render_ascii_preview(map_data),
            "Biome classification and start suitability are layered in later pipeline stages.",
        ]
    )


def _reset_hydrology_fields(map_data: MapData) -> None:
    """Clear hydrology-derived fields before recomputation."""
    for tile in map_data.tiles.values():
        tile.river_flow_to = None
        tile.flow_accumulation = 0.0
        tile.has_river = False
        tile.river_strength = 0.0


def _assign_downstream_receivers(map_data: MapData) -> dict:
    """Assign one deterministic downstream receiver per land tile."""
    upstream_map: dict = defaultdict(list)

    for coord, tile in map_data.tiles.items():
        if tile.is_water:
            continue

        downhill_land_neighbors = [
            neighbor
            for neighbor in iter_neighbor_coords(map_data, coord)
            if not map_data.tiles[neighbor].is_water
            and map_data.tiles[neighbor].elevation < (tile.elevation - DOWNHILL_EPSILON)
        ]
        coastal_water_neighbors = [
            neighbor
            for neighbor in iter_neighbor_coords(map_data, coord)
            if map_data.tiles[neighbor].is_water
        ]

        if downhill_land_neighbors:
            receiver = max(
                downhill_land_neighbors,
                key=lambda neighbor: (
                    tile.elevation - map_data.tiles[neighbor].elevation,
                    map_data.tiles[neighbor].flow_accumulation,
                    -map_data.tiles[neighbor].display_row,
                    -map_data.tiles[neighbor].display_col,
                ),
            )
            tile.river_flow_to = receiver
            upstream_map[receiver].append(coord)
        elif coastal_water_neighbors:
            tile.river_flow_to = min(
                coastal_water_neighbors,
                key=lambda neighbor: (
                    map_data.tiles[neighbor].display_row,
                    map_data.tiles[neighbor].display_col,
                ),
            )

    return upstream_map


def _accumulate_flow(map_data: MapData) -> None:
    """Accumulate weighted runoff through the full drainage graph."""
    land_coords = [coord for coord, tile in map_data.tiles.items() if not tile.is_water]

    for coord in land_coords:
        map_data.tiles[coord].flow_accumulation = _local_runoff(map_data.tiles[coord])

    ordered_coords = sorted(
        land_coords,
        key=lambda coord: (
            -map_data.tiles[coord].elevation,
            map_data.tiles[coord].display_row,
            map_data.tiles[coord].display_col,
        ),
    )

    for coord in ordered_coords:
        tile = map_data.tiles[coord]
        if tile.river_flow_to is None:
            continue

        target = map_data.tiles[tile.river_flow_to]
        if target.is_water:
            continue

        target.flow_accumulation += tile.flow_accumulation


def _mark_visible_rivers(map_data: MapData, upstream_map: dict) -> None:
    """Promote coherent river networks from major mouths upstream."""
    land_tiles = [tile for tile in map_data.tiles.values() if not tile.is_water]
    if not land_tiles:
        return

    stream_order = _compute_strahler_order(map_data, upstream_map)
    mouth_threshold, tributary_threshold = _channel_thresholds(
        map_data,
        land_tiles,
    )
    candidate_mouths = [
        tile.coord
        for tile in land_tiles
        if _is_visible_mouth(
            map_data=map_data,
            coord=tile.coord,
            mouth_threshold=mouth_threshold,
        )
    ]
    candidate_mouths.sort(
        key=lambda coord: (
            -map_data.tiles[coord].flow_accumulation,
            -stream_order.get(coord, 1),
            map_data.tiles[coord].display_row,
            map_data.tiles[coord].display_col,
        )
    )
    max_visible_tiles = max(1, int(len(land_tiles) * MAX_VISIBLE_RIVER_RATIO))
    visible_tiles: set = set()

    for mouth in candidate_mouths:
        _mark_branch_network(
            map_data=map_data,
            coord=mouth,
            upstream_map=upstream_map,
            stream_order=stream_order,
            visible_tiles=visible_tiles,
            mouth_threshold=mouth_threshold,
            tributary_threshold=tributary_threshold,
            max_visible_tiles=max_visible_tiles,
        )
        if len(visible_tiles) >= max_visible_tiles:
            break

    for coord in visible_tiles:
        tile = map_data.tiles[coord]
        tile.has_river = True
        tile.river_strength = _river_strength(tile.flow_accumulation, stream_order.get(coord, 1))


def _compute_strahler_order(map_data: MapData, upstream_map: dict) -> dict:
    """Return Strahler stream order for every routed land tile."""
    stream_order: dict = {}
    ordered_coords = sorted(
        (coord for coord, tile in map_data.tiles.items() if not tile.is_water),
        key=lambda coord: (
            map_data.tiles[coord].elevation,
            map_data.tiles[coord].display_row,
            map_data.tiles[coord].display_col,
        ),
    )

    for coord in ordered_coords:
        upstream_orders = [
            stream_order[upstream]
            for upstream in upstream_map.get(coord, [])
            if upstream in stream_order
        ]
        if not upstream_orders:
            stream_order[coord] = 1
            continue

        highest = max(upstream_orders)
        if upstream_orders.count(highest) >= 2:
            stream_order[coord] = highest + 1
        else:
            stream_order[coord] = highest

    return stream_order


def _channel_thresholds(map_data: MapData, land_tiles: list) -> tuple[float, float]:
    """Return mouth and tributary flow thresholds."""
    flows = sorted(tile.flow_accumulation for tile in land_tiles)
    mouth_index = min(len(flows) - 1, max(0, int(len(flows) * MOUTH_FLOW_QUANTILE)))
    tributary_index = min(len(flows) - 1, max(0, int(len(flows) * TRIBUTARY_FLOW_QUANTILE)))
    mouth_flow = max(
        MIN_SOURCE_FLOW,
        map_data.config.river_source_threshold,
        flows[mouth_index],
    )
    tributary_flow = max(MIN_SOURCE_FLOW * 0.72, flows[tributary_index])
    return mouth_flow, tributary_flow


def _is_visible_mouth(
    map_data: MapData,
    coord,
    mouth_threshold: float,
) -> bool:
    """Return whether a tile is a valid visible-river mouth or coastal outlet."""
    tile = map_data.tiles[coord]
    if tile.flow_accumulation < mouth_threshold:
        return False
    if tile.river_flow_to is None:
        return True

    target = map_data.tiles[tile.river_flow_to]
    if target.is_water:
        return True

    if tile.elevation < MIN_SOURCE_ELEVATION:
        return False
    return False


def _mark_branch_network(
    map_data: MapData,
    coord,
    upstream_map: dict,
    stream_order: dict,
    visible_tiles: set,
    mouth_threshold: float,
    tributary_threshold: float,
    max_visible_tiles: int,
) -> None:
    """Mark a main stem and meaningful tributaries upstream from a mouth."""
    if coord in visible_tiles or len(visible_tiles) >= max_visible_tiles:
        return

    tile = map_data.tiles[coord]
    if tile.is_water:
        return

    visible_tiles.add(coord)
    upstreams = sorted(
        upstream_map.get(coord, []),
        key=lambda upstream: (
            -map_data.tiles[upstream].flow_accumulation,
            -stream_order.get(upstream, 1),
            map_data.tiles[upstream].display_row,
            map_data.tiles[upstream].display_col,
        ),
    )
    if not upstreams:
        return

    primary = upstreams[0]
    primary_tile = map_data.tiles[primary]
    if primary_tile.flow_accumulation >= tributary_threshold and primary_tile.elevation >= MIN_SOURCE_ELEVATION:
        _mark_branch_network(
            map_data=map_data,
            coord=primary,
            upstream_map=upstream_map,
            stream_order=stream_order,
            visible_tiles=visible_tiles,
            mouth_threshold=mouth_threshold,
            tributary_threshold=tributary_threshold,
            max_visible_tiles=max_visible_tiles,
        )

    for tributary in upstreams[1:]:
        tributary_tile = map_data.tiles[tributary]
        if tributary_tile.flow_accumulation < tributary_threshold:
            continue
        if tributary_tile.elevation < MIN_SOURCE_ELEVATION:
            continue
        if tributary_tile.flow_accumulation < primary_tile.flow_accumulation * MIN_TRIBUTARY_RATIO:
            continue
        if stream_order.get(tributary, 1) < 2 and tributary_tile.flow_accumulation < mouth_threshold:
            continue
        _mark_branch_network(
            map_data=map_data,
            coord=tributary,
            upstream_map=upstream_map,
            stream_order=stream_order,
            visible_tiles=visible_tiles,
            mouth_threshold=mouth_threshold,
            tributary_threshold=tributary_threshold,
            max_visible_tiles=max_visible_tiles,
        )


def _local_runoff(tile) -> float:
    """Return weighted local runoff for one land tile."""
    upland_bonus = max(0.0, tile.elevation - 0.40)
    cold_bonus = max(0.0, 0.40 - tile.temperature)
    return (
        BASE_RUNOFF
        + (tile.moisture * MOISTURE_RUNOFF_WEIGHT)
        + (upland_bonus * UPLAND_RUNOFF_WEIGHT)
        + (cold_bonus * COLD_RUNOFF_WEIGHT)
    )


def _river_strength(flow_accumulation: float, stream_order: int) -> float:
    """Return a visible-channel strength value for rendering."""
    return max(
        1.0,
        (math.log2(max(flow_accumulation, 1.0) + 1.0) * 0.75)
        + (stream_order * RIVER_STRENGTH_SCALE * 0.25),
    )
