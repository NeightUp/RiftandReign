"""Continent-first landmask and elevation generation."""

from __future__ import annotations

from collections import deque

from rnr_mapgen.board import display_to_axial, iter_neighbor_coords
from rnr_mapgen.fields import _build_seam_profile, _seam_field, _tile_world_ratios
from rnr_mapgen.noise import clamp_unit, hash_unit_interval, wrapped_value_noise
from rnr_mapgen.types import MapData


DEFAULT_LAND_RATIO = 0.46
SEA_LEVEL_TO_LAND_RATIO_SCALE = 0.22
MIN_LAND_RATIO = 0.40
MAX_LAND_RATIO = 0.56
INITIAL_SMOOTHING_PASSES = 1
MIN_MAJOR_LAND_REGION = 4
MIN_CONTINENT_REGION = 180
MIN_INLAND_WATER_REGION = 5
MIN_MAJOR_OCEAN_REGION = 16
MIN_INLAND_SEA_REGION = 14
SEAM_REOPEN_THRESHOLD = 0.70
COASTAL_ELEVATION_BASE = 0.24
INLAND_ELEVATION_WEIGHT = 0.10
UPLIFT_WEIGHT = 0.18
RUGGEDNESS_WEIGHT = 0.64
RIDGE_DETAIL_WEIGHT = 0.10
WATER_DEPTH_WEIGHT = 0.18
RIDGE_DETAIL_SCALE = 9.0
COAST_WIDTH_THRESHOLD = 2


def classify_terrain(map_data: MapData) -> MapData:
    """Generate a continent-first landmask and final elevation field."""
    potential_scores = {coord: tile.continentality for coord, tile in map_data.tiles.items()}
    landmask = _initial_landmask(map_data, potential_scores)
    landmask = _smooth_landmask(map_data, landmask)
    _remove_small_land_regions(map_data, landmask)
    _reopen_world_seam(map_data, landmask)
    _fill_small_inland_water_regions(map_data, landmask)
    _preserve_major_ocean_breaks(map_data, landmask)

    for coord, tile in map_data.tiles.items():
        tile.is_water = not landmask[coord]

    _apply_final_elevation(map_data, potential_scores)
    _assign_water_classes(map_data)
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
            "Hydrology, biomes, and start suitability are layered in later pipeline stages.",
        ]
    )


def _initial_landmask(map_data: MapData, potential_scores: dict) -> dict:
    """Classify land from macro continent scores using an absolute cutoff with ratio guardrails."""
    adjusted_scores = {
        coord: score + _classification_jitter(map_data, coord)
        for coord, score in potential_scores.items()
    }
    target_land_ratio = clamp_unit(
        DEFAULT_LAND_RATIO + ((0.50 - map_data.config.sea_level_threshold) * SEA_LEVEL_TO_LAND_RATIO_SCALE)
    )
    target_land_ratio = max(MIN_LAND_RATIO, min(MAX_LAND_RATIO, target_land_ratio))
    base_cutoff = clamp_unit(map_data.config.sea_level_threshold - 0.05)

    landmask = {coord: adjusted_score > base_cutoff for coord, adjusted_score in adjusted_scores.items()}
    land_ratio = sum(1 for is_land in landmask.values() if is_land) / len(landmask)
    if MIN_LAND_RATIO <= land_ratio <= MAX_LAND_RATIO:
        return landmask

    ordered_scores = sorted(adjusted_scores.values())
    desired_ratio = target_land_ratio
    water_count = int(round(len(ordered_scores) * (1.0 - desired_ratio)))
    threshold_index = max(0, min(len(ordered_scores) - 1, water_count))
    fallback_cutoff = ordered_scores[threshold_index]
    return {
        coord: adjusted_score > fallback_cutoff
        for coord, adjusted_score in adjusted_scores.items()
    }


def _smooth_landmask(map_data: MapData, landmask: dict) -> dict:
    """Run simple neighborhood-majority smoothing passes on the landmask."""
    smoothed = dict(landmask)

    for _ in range(INITIAL_SMOOTHING_PASSES):
        next_mask = dict(smoothed)
        for coord in map_data.tiles:
            land_neighbors = sum(
                1
                for neighbor in iter_neighbor_coords(map_data, coord)
                if smoothed[neighbor]
            )
            if smoothed[coord] and land_neighbors <= 1:
                next_mask[coord] = False
            elif (not smoothed[coord]) and land_neighbors >= 5:
                next_mask[coord] = True
        smoothed = next_mask

    return smoothed


def _remove_small_land_regions(map_data: MapData, landmask: dict) -> None:
    """Convert tiny detached land fragments into water."""
    for region in _collect_regions(map_data, landmask, target_is_land=True):
        if len(region) >= MIN_MAJOR_LAND_REGION:
            continue
        for coord in region:
            landmask[coord] = False


def _fill_small_inland_water_regions(map_data: MapData, landmask: dict) -> None:
    """Convert tiny inland water pockets into land."""
    for region in _collect_regions(map_data, landmask, target_is_land=False):
        if len(region) >= MIN_INLAND_WATER_REGION:
            continue
        if any(_touches_display_edge(map_data, coord) for coord in region):
            continue
        for coord in region:
            landmask[coord] = True


def _reopen_world_seam(map_data: MapData, landmask: dict) -> None:
    """Keep the intended map seam as a genuine north-south ocean corridor."""
    seam = _build_seam_profile()
    for coord, tile in map_data.tiles.items():
        x_ratio, y_ratio = _tile_world_ratios(map_data, tile.display_col, tile.display_row)
        seam_value = _seam_field(seam, x_ratio)
        if seam_value < SEAM_REOPEN_THRESHOLD:
            continue
        landmask[coord] = False


def _preserve_major_ocean_breaks(map_data: MapData, landmask: dict) -> None:
    """Reopen narrow blockers between large ocean basins."""
    ocean_regions = [
        region for region in _collect_regions(map_data, landmask, target_is_land=False)
        if len(region) >= MIN_MAJOR_OCEAN_REGION
    ]
    if len(ocean_regions) < 2:
        return

    region_lookup: dict = {}
    for index, region in enumerate(ocean_regions):
        for coord in region:
            region_lookup[coord] = index

    for coord, tile in map_data.tiles.items():
        if not landmask[coord]:
            continue
        water_neighbors = [
            neighbor
            for neighbor in iter_neighbor_coords(map_data, coord)
            if neighbor in region_lookup
        ]
        touching_regions = {region_lookup[neighbor] for neighbor in water_neighbors}
        if len(water_neighbors) < 2 or len(touching_regions) < 2:
            continue
        if tile.elevation > 0.44:
            continue
        landmask[coord] = False


def _apply_final_elevation(map_data: MapData, potential_scores: dict) -> None:
    """Derive final elevation from continent structure and distance to coast."""
    coastal_distance = _distance_from_water(map_data)
    max_land_distance = max(
        (distance for coord, distance in coastal_distance.items() if not map_data.tiles[coord].is_water),
        default=1,
    )
    max_water_distance = max(
        (distance for coord, distance in coastal_distance.items() if map_data.tiles[coord].is_water),
        default=1,
    )

    for coord, tile in map_data.tiles.items():
        potential = potential_scores[coord]
        detail = wrapped_value_noise(
            map_data.seed + 991,
            "uplift_detail",
            tile.display_col / max(map_data.width - 1, 1),
            tile.display_row / max(map_data.height - 1, 1),
            RIDGE_DETAIL_SCALE,
        )

        if tile.is_water:
            water_depth = coastal_distance[coord] / max(max_water_distance, 1)
            tile.elevation = clamp_unit((potential * 0.18) - (water_depth * WATER_DEPTH_WEIGHT))
            continue

        tile.water_class = None
        tile.is_lake = False

        inland_factor = coastal_distance[coord] / max(max_land_distance, 1)
        polar_cooling = abs(((tile.display_row / max(map_data.height - 1, 1)) * 2.0) - 1.0)
        upland_shape = clamp_unit((potential - 0.32) / 0.52)
        tile.elevation = clamp_unit(
            COASTAL_ELEVATION_BASE
            + (inland_factor * INLAND_ELEVATION_WEIGHT)
            + (upland_shape * UPLIFT_WEIGHT)
            + (tile.ruggedness * RUGGEDNESS_WEIGHT)
            + ((detail - 0.5) * RIDGE_DETAIL_WEIGHT)
            - (polar_cooling * 0.07)
        )


def _distance_from_water(map_data: MapData) -> dict:
    """Return minimum tile distance to opposite terrain type."""
    distances: dict = {}
    frontier: deque = deque()

    for coord, tile in map_data.tiles.items():
        opposite_neighbor = any(
            map_data.tiles[neighbor].is_water != tile.is_water
            for neighbor in iter_neighbor_coords(map_data, coord)
        )
        if opposite_neighbor:
            distances[coord] = 0
            frontier.append(coord)

    while frontier:
        current = frontier.popleft()
        current_is_water = map_data.tiles[current].is_water
        for neighbor in iter_neighbor_coords(map_data, current):
            if map_data.tiles[neighbor].is_water != current_is_water:
                continue
            if neighbor in distances:
                continue
            distances[neighbor] = distances[current] + 1
            frontier.append(neighbor)

    for coord in map_data.tiles:
        distances.setdefault(coord, 0)

    return distances


def _collect_regions(map_data: MapData, landmask: dict, target_is_land: bool) -> list[set]:
    """Collect connected land or water regions from the current landmask."""
    regions: list[set] = []
    visited: set = set()

    for coord in map_data.tiles:
        if coord in visited or landmask[coord] != target_is_land:
            continue

        region: set = set()
        frontier: deque = deque([coord])
        visited.add(coord)

        while frontier:
            current = frontier.popleft()
            region.add(current)
            for neighbor in iter_neighbor_coords(map_data, current):
                if neighbor in visited or landmask[neighbor] != target_is_land:
                    continue
                visited.add(neighbor)
                frontier.append(neighbor)

        regions.append(region)

    return regions


def _touches_display_edge(map_data: MapData, coord) -> bool:
    """Return whether a tile touches the rectangular display edge."""
    tile = map_data.tiles[coord]
    return (
        tile.display_col == 0
        or tile.display_row == 0
        or tile.display_col == map_data.width - 1
        or tile.display_row == map_data.height - 1
    )


def _assign_water_classes(map_data: MapData) -> None:
    """Assign broad water categories for rendering and future gameplay rules."""
    coastal_distance = _distance_from_water(map_data)
    for region in _collect_regions(
        map_data,
        {coord: not tile.is_water for coord, tile in map_data.tiles.items()},
        target_is_land=False,
    ):
        touches_north_south_edge = any(
            map_data.tiles[coord].display_row in {0, map_data.height - 1}
            for coord in region
        )
        touches_east_west_edge = any(
            map_data.tiles[coord].display_col in {0, map_data.width - 1}
            for coord in region
        )
        is_ocean = touches_north_south_edge or touches_east_west_edge

        for coord in region:
            tile = map_data.tiles[coord]
            water_depth = coastal_distance[coord]
            if is_ocean:
                tile.water_class = "deep_ocean" if water_depth >= COAST_WIDTH_THRESHOLD else "coast"
                tile.is_lake = False
            elif len(region) >= MIN_INLAND_SEA_REGION:
                tile.water_class = "inland_sea"
                tile.is_lake = False
            else:
                tile.water_class = "lake"
                tile.is_lake = True


def _classification_jitter(map_data: MapData, coord) -> float:
    """Return a tiny deterministic bias to break terrain-score ties without lattice artifacts."""
    return (hash_unit_interval(map_data.seed + 1601, "terrain_jitter", coord.q, coord.r) - 0.5) * 1e-6
