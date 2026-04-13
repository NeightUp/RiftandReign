"""Deterministic continent-oriented land and water classification."""

from __future__ import annotations

from collections import deque

from rnr_mapgen.board import display_to_axial, iter_board_coords
from rnr_mapgen.hex import HexCoord
from rnr_mapgen.types import MapData


SEA_LEVEL_THRESHOLD = 0.39
NEIGHBOR_ELEVATION_WEIGHT = 0.24
COASTAL_VARIATION_WEIGHT = 0.04
ISOLATED_LAND_MAX_NEIGHBORS = 1
COHERENT_WATER_TO_LAND_NEIGHBORS = 5
LAND_JOIN_SCORE = 0.44
NARROW_LAND_MAX_NEIGHBORS = 2
NARROW_LAND_MAX_ELEVATION = 0.50
MIN_LAND_REGION_SIZE = 6
MIN_INLAND_WATER_REGION_SIZE = 4


def classify_terrain(map_data: MapData) -> MapData:
    """Classify every tile as land or water using broad continent-friendly rules."""
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

    for display_row in range(map_data.height):
        chars = [
            "#"
            if not map_data.tiles[display_to_axial(display_col, display_row)].is_water
            else "."
            for display_col in range(map_data.width)
        ]
        indent = " " if display_row % 2 else ""
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
    neighbor_elevations = [
        map_data.tiles[neighbor].elevation
        for neighbor in coord.list_neighbors()
        if neighbor in map_data.tiles
    ]
    neighbor_average = (
        sum(neighbor_elevations) / len(neighbor_elevations)
        if neighbor_elevations
        else tile.elevation
    )
    terrain_score = (
        tile.elevation
        + (NEIGHBOR_ELEVATION_WEIGHT * neighbor_average)
        + (COASTAL_VARIATION_WEIGHT * (tile.moisture - 0.5))
    )
    return terrain_score >= map_data.config.sea_level_threshold


def _cleanup_landmask(
    map_data: MapData, initial_land: dict[HexCoord, bool]
) -> dict[HexCoord, bool]:
    """Apply coherence cleanup to reduce speckle and tiny trapped regions."""
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

    _remove_small_land_regions(map_data, cleaned)
    _break_narrow_land_bridges(map_data, cleaned)
    _fill_small_inland_water_regions(map_data, cleaned)
    return cleaned


def _remove_small_land_regions(map_data: MapData, landmask: dict[HexCoord, bool]) -> None:
    """Convert tiny detached land fragments into water."""
    for region in _collect_regions(map_data, landmask, target_is_land=True):
        if len(region) >= MIN_LAND_REGION_SIZE:
            continue
        for coord in region:
            landmask[coord] = False


def _fill_small_inland_water_regions(map_data: MapData, landmask: dict[HexCoord, bool]) -> None:
    """Convert tiny fully enclosed water pockets into land."""
    for region in _collect_regions(map_data, landmask, target_is_land=False):
        if len(region) >= MIN_INLAND_WATER_REGION_SIZE:
            continue
        if any(_touches_display_edge(map_data, coord) for coord in region):
            continue
        for coord in region:
            landmask[coord] = True


def _break_narrow_land_bridges(map_data: MapData, landmask: dict[HexCoord, bool]) -> None:
    """Remove low-elevation one- and two-hex land connectors between larger masses."""
    to_water: list[HexCoord] = []

    for coord in iter_board_coords(map_data.width, map_data.height):
        if not landmask[coord]:
            continue

        land_neighbors = sum(
            1
            for neighbor in coord.list_neighbors()
            if neighbor in map_data.tiles and landmask[neighbor]
        )
        if land_neighbors > NARROW_LAND_MAX_NEIGHBORS:
            continue
        if map_data.tiles[coord].elevation > NARROW_LAND_MAX_ELEVATION:
            continue
        to_water.append(coord)

    for coord in to_water:
        landmask[coord] = False


def _collect_regions(
    map_data: MapData,
    landmask: dict[HexCoord, bool],
    target_is_land: bool,
) -> list[set[HexCoord]]:
    """Collect connected land or water regions from the current landmask."""
    regions: list[set[HexCoord]] = []
    visited: set[HexCoord] = set()

    for coord in map_data.tiles:
        if coord in visited or landmask[coord] != target_is_land:
            continue

        region: set[HexCoord] = set()
        frontier: deque[HexCoord] = deque([coord])
        visited.add(coord)

        while frontier:
            current = frontier.popleft()
            region.add(current)
            for neighbor in current.list_neighbors():
                if neighbor not in map_data.tiles:
                    continue
                if neighbor in visited or landmask[neighbor] != target_is_land:
                    continue
                visited.add(neighbor)
                frontier.append(neighbor)

        regions.append(region)

    return regions


def _touches_display_edge(map_data: MapData, coord: HexCoord) -> bool:
    """Return whether a tile touches the rectangular display edge."""
    tile = map_data.tiles[coord]
    return (
        tile.display_col == 0
        or tile.display_row == 0
        or tile.display_col == map_data.width - 1
        or tile.display_row == map_data.height - 1
    )
