"""Deterministic first-pass hydrology groundwork for the map foundation."""

from __future__ import annotations

from rnr_mapgen.hex import HexCoord
from rnr_mapgen.types import MapData

RIVER_STRENGTH_SCALE = 4.0


def generate_hydrology(map_data: MapData) -> MapData:
    """Populate first-pass downhill routing, accumulation, and river markers."""
    _reset_hydrology_fields(map_data)
    _assign_outflows(map_data)
    _accumulate_flow(map_data)
    _mark_rivers(map_data)
    return map_data


def render_ascii_preview(map_data: MapData) -> str:
    """Render a compact ASCII preview using land, water, and river markers."""
    lines: list[str] = []

    for r in range(map_data.height):
        chars: list[str] = []
        for q in range(map_data.width):
            tile = map_data.tiles[HexCoord(q=q, r=r)]
            if tile.is_water:
                chars.append(".")
            elif tile.has_river:
                chars.append("~")
            else:
                chars.append("#")

        indent = " " if r % 2 else ""
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


def _assign_outflows(map_data: MapData) -> None:
    """Assign one downhill outflow target per land tile when available."""
    for coord, tile in map_data.tiles.items():
        if tile.is_water:
            continue

        downhill_neighbors = [
            neighbor
            for neighbor in coord.list_neighbors()
            if neighbor in map_data.tiles
            and map_data.tiles[neighbor].elevation < tile.elevation
        ]
        if not downhill_neighbors:
            continue

        tile.river_flow_to = min(
            downhill_neighbors,
            key=lambda neighbor: (
                map_data.tiles[neighbor].elevation,
                neighbor.q,
                neighbor.r,
            ),
        )


def _accumulate_flow(map_data: MapData) -> None:
    """Accumulate upstream contribution in descending elevation order."""
    land_coords = [
        coord for coord, tile in map_data.tiles.items() if not tile.is_water
    ]

    for coord in land_coords:
        map_data.tiles[coord].flow_accumulation = 1.0

    ordered_coords = sorted(
        land_coords,
        key=lambda coord: (
            -map_data.tiles[coord].elevation,
            coord.q,
            coord.r,
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


def _mark_rivers(map_data: MapData) -> None:
    """Mark sparse first-pass rivers from accumulated downhill flow."""
    for tile in map_data.tiles.values():
        if tile.is_water:
            continue

        if tile.flow_accumulation < map_data.config.river_source_threshold:
            continue

        tile.has_river = True
        tile.river_strength = tile.flow_accumulation / RIVER_STRENGTH_SCALE
