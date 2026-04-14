"""Deterministic terrain-driven hydrology and visible river-network selection."""

from __future__ import annotations

import math
from collections import defaultdict

from rnr_mapgen.board import display_to_axial
from rnr_mapgen.hex import HexCoord
from rnr_mapgen.types import MapData


BASE_RUNOFF = 0.35
MOISTURE_RUNOFF_WEIGHT = 1.70
UPLAND_RUNOFF_WEIGHT = 0.55
COLD_RUNOFF_WEIGHT = 0.30
DOWNHILL_EPSILON = 1e-6
SOURCE_ELEVATION_THRESHOLD = 0.28
CHANNEL_THRESHOLD_QUANTILE = 0.78
MIN_CHANNEL_THRESHOLD = 3.0
CONTINUATION_FACTOR = 0.50
SOURCE_FACTOR = 1.00
MAX_RIVER_TILE_RATIO = 0.18
MIN_SOURCE_DISTANCE_FROM_COAST = 0
RIVER_STRENGTH_SCALE = 2.6


def generate_hydrology(map_data: MapData) -> MapData:
    """Populate downhill routing, accumulation, and selected visible river channels."""
    _reset_hydrology_fields(map_data)
    upstream_map = _assign_outflows(map_data)
    _accumulate_flow(map_data)
    _mark_rivers(map_data, upstream_map)
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
            "Biomes and start validation are not implemented yet.",
        ]
    )


def _reset_hydrology_fields(map_data: MapData) -> None:
    """Clear hydrology-derived fields before recomputation."""
    for tile in map_data.tiles.values():
        tile.river_flow_to = None
        tile.flow_accumulation = 0.0
        tile.has_river = False
        tile.river_strength = 0.0


def _assign_outflows(map_data: MapData) -> dict[HexCoord, list[HexCoord]]:
    """Assign one deterministic downstream receiver per land tile when available."""
    upstream_map: dict[HexCoord, list[HexCoord]] = defaultdict(list)

    for coord, tile in map_data.tiles.items():
        if tile.is_water:
            continue

        downhill_land_neighbors = [
            neighbor
            for neighbor in coord.list_neighbors()
            if neighbor in map_data.tiles
            and not map_data.tiles[neighbor].is_water
            and map_data.tiles[neighbor].elevation < (tile.elevation - DOWNHILL_EPSILON)
        ]
        coastal_water_neighbors = [
            neighbor
            for neighbor in coord.list_neighbors()
            if neighbor in map_data.tiles and map_data.tiles[neighbor].is_water
        ]

        if downhill_land_neighbors:
            receiver = min(
                downhill_land_neighbors,
                key=lambda neighbor: (
                    map_data.tiles[neighbor].elevation,
                    map_data.tiles[neighbor].display_row,
                    map_data.tiles[neighbor].display_col,
                ),
            )
            tile.river_flow_to = receiver
            upstream_map[receiver].append(coord)
            continue

        if coastal_water_neighbors:
            tile.river_flow_to = min(
                coastal_water_neighbors,
                key=lambda neighbor: (
                    map_data.tiles[neighbor].display_row,
                    map_data.tiles[neighbor].display_col,
                ),
            )

    return upstream_map


def _accumulate_flow(map_data: MapData) -> None:
    """Accumulate weighted runoff in descending elevation order."""
    land_coords = [
        coord for coord, tile in map_data.tiles.items() if not tile.is_water
    ]

    for coord in land_coords:
        tile = map_data.tiles[coord]
        tile.flow_accumulation = _tile_runoff(tile)

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


def _mark_rivers(map_data: MapData, upstream_map: dict[HexCoord, list[HexCoord]]) -> None:
    """Promote only significant drainage paths into visible river channels."""
    land_tiles = [tile for tile in map_data.tiles.values() if not tile.is_water]
    if not land_tiles:
        return

    threshold = _channel_threshold(map_data, land_tiles)
    continuation_threshold = threshold * CONTINUATION_FACTOR
    source_threshold = threshold * SOURCE_FACTOR
    coastal_distance = _coastal_distance(map_data)

    sources = [
        tile.coord
        for tile in land_tiles
        if _is_visible_source(
            map_data=map_data,
            coord=tile.coord,
            upstream_map=upstream_map,
            coastal_distance=coastal_distance,
            source_threshold=source_threshold,
        )
    ]
    sources.sort(
        key=lambda coord: (
            -map_data.tiles[coord].flow_accumulation,
            map_data.tiles[coord].display_row,
            map_data.tiles[coord].display_col,
        )
    )

    max_visible_tiles = max(1, int(len(land_tiles) * MAX_RIVER_TILE_RATIO))
    visible_count = 0

    for source in sources:
        current = source
        while current is not None and visible_count < max_visible_tiles:
            tile = map_data.tiles[current]
            if tile.is_water:
                break
            if tile.flow_accumulation < continuation_threshold and current != source:
                break
            if tile.has_river:
                break

            tile.has_river = True
            tile.river_strength = _river_strength(tile.flow_accumulation, continuation_threshold)
            visible_count += 1

            downstream = tile.river_flow_to
            if downstream is None:
                break
            if map_data.tiles[downstream].is_water:
                break
            current = downstream


def _tile_runoff(tile) -> float:
    """Return the weighted local runoff contribution for one land tile."""
    upland_bonus = max(0.0, tile.elevation - 0.45)
    cold_bonus = max(0.0, 0.42 - tile.temperature)
    return (
        BASE_RUNOFF
        + (tile.moisture * MOISTURE_RUNOFF_WEIGHT)
        + (upland_bonus * UPLAND_RUNOFF_WEIGHT)
        + (cold_bonus * COLD_RUNOFF_WEIGHT)
    )


def _channel_threshold(map_data: MapData, land_tiles: list) -> float:
    """Return an adaptive visible-channel threshold from flow accumulation."""
    flows = sorted(tile.flow_accumulation for tile in land_tiles)
    index = min(len(flows) - 1, max(0, int(len(flows) * CHANNEL_THRESHOLD_QUANTILE)))
    quantile_threshold = flows[index]
    return max(MIN_CHANNEL_THRESHOLD, map_data.config.river_source_threshold * 2.4, quantile_threshold)


def _is_visible_source(
    map_data: MapData,
    coord: HexCoord,
    upstream_map: dict[HexCoord, list[HexCoord]],
    coastal_distance: dict[HexCoord, int],
    source_threshold: float,
) -> bool:
    """Return whether a tile should seed a visible river channel."""
    tile = map_data.tiles[coord]
    if tile.flow_accumulation < source_threshold:
        return False
    if tile.elevation < SOURCE_ELEVATION_THRESHOLD:
        return False
    if coastal_distance.get(coord, 0) < MIN_SOURCE_DISTANCE_FROM_COAST:
        return False
    return not any(
        map_data.tiles[upstream].flow_accumulation >= source_threshold
        for upstream in upstream_map.get(coord, [])
    )


def _coastal_distance(map_data: MapData) -> dict[HexCoord, int]:
    """Return the minimum number of land steps from each land tile to coastal water."""
    distances: dict[HexCoord, int] = {}
    frontier: list[HexCoord] = []

    for coord, tile in map_data.tiles.items():
        if tile.is_water:
            continue
        if any(
            neighbor in map_data.tiles and map_data.tiles[neighbor].is_water
            for neighbor in coord.list_neighbors()
        ):
            distances[coord] = 0
            frontier.append(coord)

    index = 0
    while index < len(frontier):
        current = frontier[index]
        index += 1
        for neighbor in current.list_neighbors():
            if neighbor not in map_data.tiles or map_data.tiles[neighbor].is_water:
                continue
            if neighbor in distances:
                continue
            distances[neighbor] = distances[current] + 1
            frontier.append(neighbor)

    return distances


def _river_strength(flow_accumulation: float, continuation_threshold: float) -> float:
    """Return a compact visible strength value for selected river tiles."""
    ratio = max(1.0, flow_accumulation / max(continuation_threshold, 1.0))
    return max(1.0, math.log2(ratio + 1.0) * RIVER_STRENGTH_SCALE / 2.0)
