"""Deterministic continent-first scalar-field generation."""

from __future__ import annotations

import math
from dataclasses import dataclass

from rnr_mapgen.noise import clamp_unit, hash_unit_interval, wrapped_fbm_noise, wrapped_value_noise
from rnr_mapgen.types import MapData


MAIN_CONTINENT_MIN = 2
MAIN_CONTINENT_MAX = 4
CONTINENT_BLOBS_MIN = 5
CONTINENT_BLOBS_MAX = 8
ISLAND_GROUP_MIN = 4
ISLAND_GROUP_MAX = 8
RIDGE_LOBES_MIN = 4
RIDGE_LOBES_MAX = 7

CONTINENT_WEIGHT = 0.94
ISLAND_WEIGHT = 0.22
BASIN_CARVE_WEIGHT = 0.14
DETAIL_WEIGHT = 0.10
SEAM_ATTENUATION = 0.82
POLAR_ATTENUATION = 0.34

RUGGED_CHAIN_WEIGHT = 0.68
RUGGED_NOISE_WEIGHT = 0.22
RUGGED_DETAIL_WEIGHT = 0.10

MOISTURE_SCALE = 2.4
MOISTURE_DETAIL_SCALE = 6.8
TEMPERATURE_SCALE = 2.0
TEMPERATURE_DETAIL_SCALE = 5.4
RUGGED_NOISE_SCALE = 4.0
RUGGED_DETAIL_SCALE = 8.5

MOISTURE_NOISE_WEIGHT = 0.34
MOISTURE_DETAIL_WEIGHT = 0.16
MOISTURE_LATITUDE_WEIGHT = 0.08
MOISTURE_WATER_WEIGHT = 0.24
MOISTURE_DRY_INTERIOR_WEIGHT = 0.18
TEMPERATURE_LATITUDE_WEIGHT = 0.56
TEMPERATURE_NOISE_WEIGHT = 0.18
TEMPERATURE_DETAIL_WEIGHT = 0.10
TEMPERATURE_OCEAN_MODERATION_WEIGHT = 0.08
TEMPERATURE_RUGGEDNESS_WEIGHT = 0.08

SEAM_WIDTH = 0.07
SEAM_GAP = 0.06
POLAR_START = 0.90
USABLE_LATITUDE_MIN = 0.18
USABLE_LATITUDE_MAX = 0.82
ANCHOR_CANDIDATE_COUNT = 48
SQRT_3 = math.sqrt(3.0)


@dataclass(frozen=True, slots=True)
class Lobe:
    """Broad deterministic field lobe."""

    x: float
    y: float
    radius_x: float
    radius_y: float
    strength: float


@dataclass(frozen=True, slots=True)
class SeamProfile:
    """Preferred ocean seam running north to south."""

    center_x: float
    width: float


@dataclass(frozen=True, slots=True)
class ContinentRegion:
    """One organic continent assembled from several blobs."""

    center_x: float
    center_y: float
    blobs: tuple[Lobe, ...]


def generate_scalar_fields(map_data: MapData) -> MapData:
    """Populate deterministic continent potential, ruggedness, moisture, and temperature."""
    seam = _build_seam_profile()
    continent_regions = _build_continent_regions(map_data, seam)
    island_groups = _build_ocean_island_lobes(map_data, seam, continent_regions)
    ridge_lobes = _build_ridge_lobes(map_data, seam, continent_regions)

    for tile in map_data.tiles.values():
        x_ratio, y_ratio = _tile_world_ratios(map_data, tile.display_col, tile.display_row)
        continentality = _build_landmass_potential(
            map_data=map_data,
            seam=seam,
            x_ratio=x_ratio,
            y_ratio=y_ratio,
            continent_regions=continent_regions,
            island_groups=island_groups,
        )
        ruggedness = _build_ruggedness(
            map_data=map_data,
            x_ratio=x_ratio,
            y_ratio=y_ratio,
            continentality=continentality,
            ridge_lobes=ridge_lobes,
        )

        tile.continentality = continentality
        tile.ruggedness = ruggedness
        tile.elevation = continentality
        tile.moisture = _build_moisture_value(map_data, x_ratio, y_ratio, continentality, ruggedness)
        tile.temperature = _build_temperature_value(map_data, x_ratio, y_ratio, continentality, ruggedness)

    return map_data


def _build_landmass_potential(
    map_data: MapData,
    seam: SeamProfile,
    x_ratio: float,
    y_ratio: float,
    continent_regions: list[ContinentRegion],
    island_groups: list[Lobe],
) -> float:
    """Return macro continent potential used by terrain classification."""
    continent_field = _continent_field(continent_regions, x_ratio, y_ratio)
    island_field = _lobe_field(island_groups, x_ratio, y_ratio)
    warped_x, warped_y = _warp_coords(map_data, x_ratio, y_ratio, "continent")
    basin_carve = wrapped_fbm_noise(map_data.seed + 401, "ocean_basin", warped_x, warped_y, 1.8, octaves=3)
    detail = wrapped_fbm_noise(map_data.seed + 421, "continent_detail", warped_x, warped_y, 5.4, octaves=3)
    seam_field = _seam_field(seam, x_ratio)
    polar_factor = max(0.0, (abs((y_ratio * 2.0) - 1.0) - POLAR_START) / (1.0 - POLAR_START))

    base_land = (
        (continent_field * CONTINENT_WEIGHT)
        + (island_field * ISLAND_WEIGHT)
        + (detail * DETAIL_WEIGHT)
        - (basin_carve * BASIN_CARVE_WEIGHT)
    )
    land = clamp_unit(base_land)
    land *= max(0.0, 1.0 - (seam_field * SEAM_ATTENUATION))
    land *= max(0.0, 1.0 - (polar_factor * POLAR_ATTENUATION))
    return clamp_unit(land)


def _build_ruggedness(
    map_data: MapData,
    x_ratio: float,
    y_ratio: float,
    continentality: float,
    ridge_lobes: list[Lobe],
) -> float:
    """Return coherent ridge and upland signal."""
    ridge_field = _lobe_field(ridge_lobes, x_ratio, y_ratio)
    warped_x, warped_y = _warp_coords(map_data, x_ratio, y_ratio, "rugged")
    rugged_noise = wrapped_fbm_noise(map_data.seed + 563, "ridge_noise", warped_x, warped_y, RUGGED_NOISE_SCALE, octaves=3)
    rugged_detail = wrapped_fbm_noise(map_data.seed + 577, "ridge_detail", warped_x, warped_y, RUGGED_DETAIL_SCALE, octaves=2)
    interior_bias = clamp_unit((continentality - 0.18) / 0.60)
    value = (
        (ridge_field * RUGGED_CHAIN_WEIGHT)
        + (rugged_noise * RUGGED_NOISE_WEIGHT)
        + (rugged_detail * RUGGED_DETAIL_WEIGHT)
    ) * (0.22 + (interior_bias * 0.78))
    return clamp_unit(value)


def _build_moisture_value(
    map_data: MapData,
    x_ratio: float,
    y_ratio: float,
    continentality: float,
    ruggedness: float,
) -> float:
    """Return broad moisture values with less visible latitude banding."""
    warped_x, warped_y = _warp_coords(map_data, x_ratio, y_ratio, "moisture")
    macro_noise = wrapped_fbm_noise(map_data.seed + 701, "moisture", warped_x, warped_y, MOISTURE_SCALE, octaves=4)
    detail_noise = wrapped_fbm_noise(
        map_data.seed + 719,
        "moisture_detail",
        (warped_x + 0.17) % 1.0,
        warped_y,
        MOISTURE_DETAIL_SCALE,
        octaves=3,
        persistence=0.55,
    )
    latitude_humidity = 1.0 - abs(((y_ratio * 2.0) - 1.0) * 0.92)
    ocean_influence = 1.0 - clamp_unit((continentality - 0.10) / 0.75)
    dry_interior = clamp_unit((continentality - 0.42) / 0.38)
    rain_shadow = max(0.0, ruggedness - 0.52)
    return clamp_unit(
        (macro_noise * MOISTURE_NOISE_WEIGHT)
        + (detail_noise * MOISTURE_DETAIL_WEIGHT)
        + (latitude_humidity * MOISTURE_LATITUDE_WEIGHT)
        + (ocean_influence * MOISTURE_WATER_WEIGHT)
        - (dry_interior * MOISTURE_DRY_INTERIOR_WEIGHT)
        - (rain_shadow * 0.10)
    )


def _build_temperature_value(
    map_data: MapData,
    x_ratio: float,
    y_ratio: float,
    continentality: float,
    ruggedness: float,
) -> float:
    """Return a latitude-led temperature field with stronger regional breakup."""
    latitude_distance = abs((y_ratio * 2.0) - 1.0)
    equator_heat = 1.0 - latitude_distance
    warped_x, warped_y = _warp_coords(map_data, x_ratio, y_ratio, "temperature")
    macro_noise = wrapped_fbm_noise(map_data.seed + 801, "temperature", warped_x, warped_y, TEMPERATURE_SCALE, octaves=4)
    detail_noise = wrapped_fbm_noise(
        map_data.seed + 829,
        "temperature_detail",
        (warped_x + 0.09) % 1.0,
        warped_y,
        TEMPERATURE_DETAIL_SCALE,
        octaves=3,
    )
    ocean_moderation = 1.0 - clamp_unit((continentality - 0.08) / 0.80)
    temperature = (
        (equator_heat * TEMPERATURE_LATITUDE_WEIGHT)
        + (macro_noise * TEMPERATURE_NOISE_WEIGHT)
        + (detail_noise * TEMPERATURE_DETAIL_WEIGHT)
        + (ocean_moderation * TEMPERATURE_OCEAN_MODERATION_WEIGHT)
        + ((1.0 - ruggedness) * TEMPERATURE_RUGGEDNESS_WEIGHT)
    )
    return clamp_unit(temperature)


def _build_continent_regions(map_data: MapData, seam: SeamProfile) -> list[ContinentRegion]:
    """Return organic continents built from warped blob chains."""
    count = _continent_count(map_data)
    anchors = _select_continent_anchors(map_data, seam, count)
    regions: list[ContinentRegion] = []

    for index, (center_x, center_y) in enumerate(anchors):
        blob_count = _range_count(map_data.seed + 101 + index, CONTINENT_BLOBS_MIN, CONTINENT_BLOBS_MAX, "continent_blobs")
        heading = hash_unit_interval(map_data.seed + 131, "continent_heading", index, 0) * math.tau
        step_size = 0.035 + (0.02 * hash_unit_interval(map_data.seed + 141, "continent_step", index, 1))
        current_x = center_x
        current_y = center_y
        blobs: list[Lobe] = []

        for blob_index in range(blob_count):
            radius_x = 0.065 + (0.03 * hash_unit_interval(map_data.seed + 151, "continent_rx", index, blob_index))
            radius_y = 0.055 + (0.03 * hash_unit_interval(map_data.seed + 161, "continent_ry", index, blob_index))
            strength = 0.70 + (0.22 * hash_unit_interval(map_data.seed + 171, "continent_strength", index, blob_index))
            blobs.append(
                Lobe(
                    x=current_x,
                    y=current_y,
                    radius_x=radius_x,
                    radius_y=radius_y,
                    strength=strength,
                )
            )

            if hash_unit_interval(map_data.seed + 181, "continent_side_blob", index, blob_index) > 0.58:
                side_angle = heading + (math.pi / 2.0)
                side_sign = -1.0 if hash_unit_interval(map_data.seed + 191, "continent_side_sign", index, blob_index) < 0.5 else 1.0
                offset = 0.025 + (0.018 * hash_unit_interval(map_data.seed + 201, "continent_side_offset", index, blob_index))
                blobs.append(
                    Lobe(
                        x=(current_x + (math.cos(side_angle) * offset * side_sign)) % 1.0,
                        y=min(
                            USABLE_LATITUDE_MAX,
                            max(USABLE_LATITUDE_MIN, current_y + (math.sin(side_angle) * offset * side_sign * 0.8)),
                        ),
                        radius_x=radius_x * 0.72,
                        radius_y=radius_y * 0.72,
                        strength=strength * 0.85,
                    )
                )

            heading += (hash_unit_interval(map_data.seed + 211, "continent_turn", index, blob_index) - 0.5) * 1.4
            current_x = (current_x + (math.cos(heading) * step_size)) % 1.0
            current_y = min(
                USABLE_LATITUDE_MAX,
                max(USABLE_LATITUDE_MIN, current_y + (math.sin(heading) * step_size * 0.72)),
            )

        regions.append(
            ContinentRegion(
                center_x=center_x,
                center_y=center_y,
                blobs=tuple(blobs),
            )
        )

    return regions


def _build_ocean_island_lobes(
    map_data: MapData,
    seam: SeamProfile,
    regions: list[ContinentRegion],
) -> list[Lobe]:
    """Return islands and archipelagos chosen from ocean gaps."""
    count = _range_count(map_data.seed + 301, ISLAND_GROUP_MIN, ISLAND_GROUP_MAX, "island_group_count")
    candidate_points = _sample_ocean_gap_candidates(map_data, seam, regions)
    chosen: list[tuple[float, float]] = []
    islands: list[Lobe] = []

    while candidate_points and len(chosen) < count:
        best = max(
            candidate_points,
            key=lambda item: item[2] + (min((_candidate_distance(item, other) for other in chosen), default=1.0) * 0.35),
        )
        chosen.append((best[0], best[1]))
        candidate_points.remove(best)

    for index, (x_value, y_value) in enumerate(chosen):
        chain_count = _range_count(map_data.seed + 331 + index, 1, 3, "island_chain")
        heading = hash_unit_interval(map_data.seed + 341, "island_heading", index, 0) * math.tau
        step = 0.018 + (0.015 * hash_unit_interval(map_data.seed + 351, "island_step", index, 1))
        current_x = x_value
        current_y = y_value
        for blob_index in range(chain_count):
            islands.append(
                Lobe(
                    x=current_x,
                    y=current_y,
                    radius_x=0.018 + (0.012 * hash_unit_interval(map_data.seed + 361, "island_rx", index, blob_index)),
                    radius_y=0.016 + (0.012 * hash_unit_interval(map_data.seed + 371, "island_ry", index, blob_index)),
                    strength=0.34 + (0.18 * hash_unit_interval(map_data.seed + 381, "island_strength", index, blob_index)),
                )
            )
            heading += (hash_unit_interval(map_data.seed + 391, "island_turn", index, blob_index) - 0.5) * 1.1
            current_x = (current_x + (math.cos(heading) * step)) % 1.0
            current_y = min(0.88, max(0.12, current_y + (math.sin(heading) * step * 0.7)))

    return islands


def _build_ridge_lobes(
    map_data: MapData,
    seam: SeamProfile,
    regions: list[ContinentRegion],
) -> list[Lobe]:
    """Return coherent ridge chains embedded in continent interiors."""
    ridge_lobes: list[Lobe] = []

    for index, region in enumerate(regions):
        region_center = _region_center(region)
        chain_count = 1 if hash_unit_interval(map_data.seed + 501, "ridge_chain_count", index, 0) < 0.56 else 2
        for chain_index in range(chain_count):
            heading = hash_unit_interval(map_data.seed + 511, "ridge_heading", index, chain_index) * math.tau
            step = 0.028 + (0.014 * hash_unit_interval(map_data.seed + 521, "ridge_step", index, chain_index))
            current_x = _point_away_from_seam(
                seam,
                region_center[0] + ((hash_unit_interval(map_data.seed + 531, "ridge_x", index, chain_index) - 0.5) * 0.10),
                min_gap=SEAM_GAP,
            )
            current_y = min(
                0.82,
                max(0.18, region_center[1] + ((hash_unit_interval(map_data.seed + 541, "ridge_y", index, chain_index) - 0.5) * 0.12)),
            )
            lobe_count = _range_count(map_data.seed + 551 + chain_index, RIDGE_LOBES_MIN, RIDGE_LOBES_MAX, "ridge_lobes")

            for lobe_index in range(lobe_count):
                ridge_lobes.append(
                    Lobe(
                        x=current_x,
                        y=current_y,
                        radius_x=0.026 + (0.016 * hash_unit_interval(map_data.seed + 561, "ridge_rx", index, lobe_index)),
                        radius_y=0.030 + (0.018 * hash_unit_interval(map_data.seed + 571, "ridge_ry", index, lobe_index)),
                        strength=0.70 + (0.20 * hash_unit_interval(map_data.seed + 581, "ridge_strength", index, lobe_index)),
                    )
                )
                heading += (hash_unit_interval(map_data.seed + 591, "ridge_turn", index, lobe_index) - 0.5) * 0.95
                current_x = _point_away_from_seam(seam, current_x + (math.cos(heading) * step), min_gap=SEAM_GAP)
                current_y = min(0.84, max(0.16, current_y + (math.sin(heading) * step * 0.8)))

    return ridge_lobes


def _build_seam_profile() -> SeamProfile:
    """Return the preferred ocean seam at the world boundary."""
    return SeamProfile(center_x=0.0, width=SEAM_WIDTH)


def _continent_field(regions: list[ContinentRegion], x_ratio: float, y_ratio: float) -> float:
    """Return the strongest continent influence at one point."""
    influence = 0.0
    for region in regions:
        influence = max(influence, _lobe_field(list(region.blobs), x_ratio, y_ratio))
    return clamp_unit(influence)


def _select_continent_anchors(
    map_data: MapData,
    seam: SeamProfile,
    count: int,
) -> list[tuple[float, float]]:
    """Select continent anchors with wide separation but without latitude striping."""
    candidates: list[tuple[float, float]] = []
    for index in range(ANCHOR_CANDIDATE_COUNT):
        x_value = _point_away_from_seam(
            seam,
            0.02 + (0.96 * hash_unit_interval(map_data.seed + 611, "anchor_x", index, 0)),
            min_gap=SEAM_GAP,
        )
        y_value = USABLE_LATITUDE_MIN + (
            (USABLE_LATITUDE_MAX - USABLE_LATITUDE_MIN)
            * hash_unit_interval(map_data.seed + 621, "anchor_y", index, 1)
        )
        candidates.append((x_value, y_value))

    chosen: list[tuple[float, float]] = []
    while candidates and len(chosen) < count:
        if not chosen:
            best = max(
                candidates,
                key=lambda item: (
                    _wrapped_distance(item[0], seam.center_x),
                    0.28 - abs(item[1] - 0.50),
                ),
            )
        else:
            best = max(
                candidates,
                key=lambda item: (
                    min(_candidate_distance(item, other) for other in chosen),
                    0.18 - abs(item[1] - 0.50),
                ),
            )
        chosen.append(best)
        candidates.remove(best)

    return chosen


def _continent_count(map_data: MapData) -> int:
    """Return a weighted deterministic count where two continents are most common."""
    roll = hash_unit_interval(map_data.seed + 641, "main_count_roll", 0, 0)
    if roll < 0.54:
        return 2
    if roll < 0.84:
        return 3
    return 4


def _sample_ocean_gap_candidates(
    map_data: MapData,
    seam: SeamProfile,
    regions: list[ContinentRegion],
) -> list[tuple[float, float, float]]:
    """Return candidate island seeds from ocean gaps."""
    candidates: list[tuple[float, float, float]] = []
    for index in range(ANCHOR_CANDIDATE_COUNT):
        x_value = _point_away_from_seam(
            seam,
            0.02 + (0.96 * hash_unit_interval(map_data.seed + 651, "island_candidate_x", index, 0)),
            min_gap=0.03,
        )
        y_value = 0.16 + (0.68 * hash_unit_interval(map_data.seed + 661, "island_candidate_y", index, 1))
        continent_strength = _continent_field(regions, x_value, y_value)
        score = (1.0 - continent_strength) - (0.15 * _seam_field(seam, x_value))
        candidates.append((x_value, y_value, score))
    return candidates


def _region_center(region: ContinentRegion) -> tuple[float, float]:
    """Return the average blob center for a region."""
    if not region.blobs:
        return region.center_x, region.center_y
    x_total = 0.0
    y_total = 0.0
    for blob in region.blobs:
        x_total += blob.x
        y_total += blob.y
    return x_total / len(region.blobs), y_total / len(region.blobs)


def _lobe_field(lobes: list[Lobe], x_ratio: float, y_ratio: float) -> float:
    """Combine several broad lobes into one normalized field."""
    influence = 0.0
    for lobe in lobes:
        x_distance = _wrapped_distance(x_ratio, lobe.x) / lobe.radius_x
        y_distance = (y_ratio - lobe.y) / lobe.radius_y
        distance_squared = (x_distance * x_distance) + (y_distance * y_distance)
        if distance_squared >= 1.0:
            continue
        influence = max(influence, ((1.0 - distance_squared) ** 2) * lobe.strength)
    return clamp_unit(influence)


def _seam_field(seam: SeamProfile, x_ratio: float) -> float:
    """Return seam influence for a point on the wrapped world strip."""
    distance = _wrapped_distance(x_ratio, seam.center_x)
    if distance >= seam.width:
        return 0.0
    normalized = 1.0 - (distance / seam.width)
    return normalized * normalized * (3.0 - (2.0 * normalized))


def _range_count(seed: int, minimum: int, maximum: int, label: str) -> int:
    """Return a deterministic integer count in an inclusive range."""
    span = maximum - minimum + 1
    value = int(hash_unit_interval(seed, label, 0, 0) * span)
    return minimum + min(span - 1, value)


def _point_away_from_seam(seam: SeamProfile, x_value: float, min_gap: float) -> float:
    """Shift an x position away from the seam corridor if needed."""
    x_value = x_value % 1.0
    if _wrapped_distance(x_value, seam.center_x) >= (seam.width + min_gap):
        return x_value
    boundary = seam.width + min_gap
    return boundary if x_value < 0.5 else 1.0 - boundary


def _wrapped_distance(a: float, b: float) -> float:
    """Return wrapped x-axis distance on the 0..1 world strip."""
    raw = abs(a - b)
    return min(raw, 1.0 - raw)


def _candidate_distance(a: tuple[float, float] | tuple[float, float, float], b: tuple[float, float] | tuple[float, float, float]) -> float:
    """Return wrapped distance between two candidate points."""
    return math.hypot(_wrapped_distance(a[0], b[0]), abs(a[1] - b[1]))


def _warp_coords(map_data: MapData, x_ratio: float, y_ratio: float, label: str) -> tuple[float, float]:
    """Warp world-space sample coordinates to reduce large-scale directional artifacts."""
    warp_x = wrapped_value_noise(map_data.seed + 901, f"{label}_warp_x", x_ratio, y_ratio, 2.1) - 0.5
    warp_y = wrapped_value_noise(map_data.seed + 911, f"{label}_warp_y", x_ratio, y_ratio, 2.7) - 0.5
    return (x_ratio + (warp_x * 0.10)) % 1.0, max(0.0, min(1.0, y_ratio + (warp_y * 0.08)))


def _tile_world_ratios(map_data: MapData, display_col: int, display_row: int) -> tuple[float, float]:
    """Return cylindrical world-space ratios derived from actual hex-center positions."""
    center_x = SQRT_3 * (display_col + (0.5 if display_row & 1 else 0.0))
    center_y = 1.5 * display_row
    wrap_width = SQRT_3 * map_data.width
    max_height = max(1.5 * max(map_data.height - 1, 1), 1.0)
    x_ratio = (center_x % wrap_width) / wrap_width
    y_ratio = center_y / max_height
    return x_ratio, max(0.0, min(1.0, y_ratio))
