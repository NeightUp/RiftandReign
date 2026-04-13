"""Deterministic first-pass terrain classification for the map foundation."""

from __future__ import annotations

from rnr_mapgen.board import iter_board_coords
from rnr_mapgen.hex import HexCoord
from rnr_mapgen.types import MapData


SEA_LEVEL_THRESHOLD = 0.39
EDGE_WATER_WEIGHT = 0.09
MOISTURE_SUPPORT_WEIGHT = 0.03
TEMPERATURE_SUPPORT_WEIGHT = 0.01
LAND_JOIN_SCORE = 0.37
ISOLATED_LAND_MAX_NEIGHBORS = 1
COHERENT_WATER_TO_LAND_NEIGHBORS = 5


def classify_terrain(map_data: MapData) -> MapData:
    """Classify every tile as land or water using deterministic first-pass rules."""
    initial_land = {
        coord: _is_land_candidate(map_data, coord) for coord in map_data.tiles
    }
    cleaned_land = _cleanup_landmask(map_data, initial_land)

    for coord, tile in map_data.tiles.items():
        tile.is_water = not cleaned_land[coord]

    return map_data


def render_ascii_terrain(map_data: MapData) -> str:
    """Render a compact ASCII preview using `#` for land and `.` for water."""
    lines: list[str] = []

    for r in range(map_data.height):
        chars = [
            "#" if not map_data.tiles[HexCoord(q=q, r=r)].is_water else "."
            for q in range(map_data.width)
        ]
        indent = " " if r % 2 else ""
        lines.append(f"{indent}{''.join(chars)}")

    return "\n".join(lines)


def summarize_terrain(map_data: MapData) -> str:
    """Return a concise terrain summary including scalar ranges and ASCII preview."""
    elevation_values = [tile.elevation for tile in map_data.tiles.values()]
    moisture_values = [tile.moisture for tile in map_data.tiles.values()]
    temperature_values = [tile.temperature for tile in map_data.tiles.values()]
    land_tiles = sum(1 for tile in map_data.tiles.values() if not tile.is_water)
    water_tiles = map_data.tile_count - land_tiles
    land_percentage = (land_tiles / map_data.tile_count) * 100.0

    return "\n".join(
        [
            "RiftandReign terrain classification first pass.",
            f"Dimensions: {map_data.width}x{map_data.height}",
            f"Seed: {map_data.seed}",
            f"Total tiles: {map_data.tile_count}",
            f"Land tiles: {land_tiles}",
            f"Water tiles: {water_tiles}",
            f"Land percentage: {land_percentage:.1f}%",
            f"Elevation range: {min(elevation_values):.3f}..{max(elevation_values):.3f}",
            f"Moisture range: {min(moisture_values):.3f}..{max(moisture_values):.3f}",
            (
                "Temperature range: "
                f"{min(temperature_values):.3f}..{max(temperature_values):.3f}"
            ),
            "ASCII terrain preview:",
            render_ascii_terrain(map_data),
            "Rivers, hydrology, biomes, and start validation are not implemented yet.",
        ]
    )


def _is_land_candidate(map_data: MapData, coord: HexCoord) -> bool:
    """Return the initial land or water decision for one tile."""
    tile = map_data.tiles[coord]
    q_ratio = _axis_ratio(coord.q, map_data.width)
    r_ratio = _axis_ratio(coord.r, map_data.height)
    edge_bias = max(abs((q_ratio * 2.0) - 1.0), abs((r_ratio * 2.0) - 1.0))

    terrain_score = (
        tile.elevation
        - (EDGE_WATER_WEIGHT * edge_bias)
        + (MOISTURE_SUPPORT_WEIGHT * tile.moisture)
        + (TEMPERATURE_SUPPORT_WEIGHT * tile.temperature)
    )
    return terrain_score >= map_data.config.sea_level_threshold


def _cleanup_landmask(
    map_data: MapData, initial_land: dict[HexCoord, bool]
) -> dict[HexCoord, bool]:
    """Apply a light coherence pass to reduce single-tile terrain noise."""
    cleaned = dict(initial_land)

    for coord in iter_board_coords(map_data.width, map_data.height):
        land_neighbors = sum(
            1
            for neighbor in coord.list_neighbors()
            if neighbor in map_data.tiles and initial_land[neighbor]
        )
        tile = map_data.tiles[coord]

        if initial_land[coord] and land_neighbors <= ISOLATED_LAND_MAX_NEIGHBORS:
            cleaned[coord] = False
        elif (
            not initial_land[coord]
            and land_neighbors >= COHERENT_WATER_TO_LAND_NEIGHBORS
            and tile.elevation >= LAND_JOIN_SCORE
        ):
            cleaned[coord] = True

    return cleaned


def _axis_ratio(index: int, size: int) -> float:
    """Convert a board index into a stable 0.0..1.0 ratio."""
    if size <= 1:
        return 0.5
    return index / (size - 1)
