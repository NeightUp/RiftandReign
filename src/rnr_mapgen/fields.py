"""Deterministic continent-first scalar-field generation."""

from __future__ import annotations

import math
from dataclasses import dataclass

from rnr_mapgen.noise import clamp_unit, hash_unit_interval, wrapped_fbm_noise, wrapped_value_noise
from rnr_mapgen.types import MapData


MAIN_CONTINENT_MIN = 2
MAIN_CONTINENT_MAX = 4
ISLAND_GROUP_MIN = 3
ISLAND_GROUP_MAX = 7
REGION_LOBES_MIN = 4
REGION_LOBES_MAX = 7
RIDGE_CLUSTER_MIN = 6
RIDGE_CLUSTER_MAX = 10

MAIN_REGION_WEIGHT = 0.74
ISLAND_GROUP_WEIGHT = 0.14
BASIN_RELIEF_WEIGHT = 0.10
DETAIL_WEIGHT = 0.06
SEAM_ATTENUATION = 0.96
POLAR_OCEAN_ATTENUATION = 0.28

RUGGED_CLUSTER_WEIGHT = 0.60
RUGGED_NOISE_WEIGHT = 0.24
RUGGED_DETAIL_WEIGHT = 0.16

MOISTURE_SCALE = 3.0
MOISTURE_DETAIL_SCALE = 7.5
TEMPERATURE_SCALE = 2.4
TEMPERATURE_DETAIL_SCALE = 6.4
RUGGED_NOISE_SCALE = 4.2
RUGGED_DETAIL_SCALE = 9.0

MOISTURE_NOISE_WEIGHT = 0.40
MOISTURE_DETAIL_WEIGHT = 0.20
MOISTURE_LATITUDE_WEIGHT = 0.14
MOISTURE_WATER_BIAS_WEIGHT = 0.18
MOISTURE_WARP_WEIGHT = 0.08
TEMPERATURE_LATITUDE_WEIGHT = 0.72
TEMPERATURE_NOISE_WEIGHT = 0.10
TEMPERATURE_DETAIL_WEIGHT = 0.08
TEMPERATURE_RUGGEDNESS_WEIGHT = 0.08

SEAM_EDGE_MARGIN = 0.08
SEAM_WIDTH_MIN = 0.10
SEAM_WIDTH_MAX = 0.14
SQRT_3 = math.sqrt(3.0)
ANCHOR_LATITUDE_BANDS = (0.28, 0.42, 0.58, 0.72)


@dataclass(frozen=True, slots=True)
class Lobe:
    """Broad deterministic land, island, or ruggedness lobe."""

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
    sway: float
    tilt: float


@dataclass(frozen=True, slots=True)
class ContinentRegion:
    """One bounded continent-scale region."""

    center_x: float
    center_y: float
    radius_x: float
    radius_y: float
    strength: float
    lobes: tuple[Lobe, ...]


def generate_scalar_fields(map_data: MapData) -> MapData:
    """Populate deterministic continent potential, ruggedness, moisture, and temperature."""
    seam = _build_seam_profile(map_data)
    continent_regions = _build_continent_regions(map_data, seam)
    island_groups = _build_island_group_lobes(map_data, seam, continent_regions)
    rugged_clusters = _build_ruggedness_lobes(map_data, seam, continent_regions)

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
            rugged_clusters=rugged_clusters,
        )

        tile.continentality = continentality
        tile.ruggedness = ruggedness
        tile.elevation = clamp_unit(continentality)
        tile.moisture = _build_moisture_value(map_data, x_ratio, y_ratio, continentality)
        tile.temperature = _build_temperature_value(map_data, x_ratio, y_ratio, ruggedness)

    return map_data


def _build_landmass_potential(
    map_data: MapData,
    seam: SeamProfile,
    x_ratio: float,
    y_ratio: float,
    continent_regions: list[ContinentRegion],
    island_groups: list[Lobe],
) -> float:
    """Return a macro landmass potential used by terrain classification."""
    main_field = _continent_region_field(continent_regions, x_ratio, y_ratio)
    island_field = _lobe_field(island_groups, x_ratio, y_ratio)
    basin_field = wrapped_value_noise(map_data.seed + 401, "ocean_basin", x_ratio, y_ratio, 2.8)
    detail_field = wrapped_value_noise(map_data.seed + 431, "continent_detail", x_ratio, y_ratio, 6.0)
    seam_field = _seam_field(seam, x_ratio, y_ratio)
    polar_ocean_bias = max(0.0, abs((y_ratio * 2.0) - 1.0) - 0.52)

    base_land = clamp_unit(
        (main_field * MAIN_REGION_WEIGHT)
        + (island_field * ISLAND_GROUP_WEIGHT)
        + ((1.0 - basin_field) * BASIN_RELIEF_WEIGHT)
        + (detail_field * DETAIL_WEIGHT)
    )
    seam_multiplier = max(0.0, 1.0 - (seam_field * SEAM_ATTENUATION))
    polar_multiplier = max(0.0, 1.0 - (polar_ocean_bias * POLAR_OCEAN_ATTENUATION))
    return clamp_unit(base_land * seam_multiplier * polar_multiplier)


def _build_ruggedness(
    map_data: MapData,
    x_ratio: float,
    y_ratio: float,
    continentality: float,
    rugged_clusters: list[Lobe],
) -> float:
    """Return a secondary ruggedness field for mountain ranges and uplands."""
    cluster_field = _lobe_field(rugged_clusters, x_ratio, y_ratio)
    warped_x, warped_y = _warp_coords(map_data, x_ratio, y_ratio, "rugged")
    rugged_noise = 1.0 - abs(
        (wrapped_fbm_noise(map_data.seed + 563, "ridge_noise", warped_x, warped_y, RUGGED_NOISE_SCALE, octaves=3) * 2.0) - 1.0
    )
    detail_noise = wrapped_fbm_noise(
        map_data.seed + 577,
        "ridge_detail",
        warped_x,
        warped_y,
        RUGGED_DETAIL_SCALE,
        octaves=3,
    )
    interior_bias = max(0.0, continentality - 0.22)
    return clamp_unit(
        ((cluster_field * RUGGED_CLUSTER_WEIGHT) + (rugged_noise * RUGGED_NOISE_WEIGHT) + (detail_noise * RUGGED_DETAIL_WEIGHT))
        * (0.30 + interior_bias)
    )


def _build_moisture_value(map_data: MapData, x_ratio: float, y_ratio: float, continentality: float) -> float:
    """Return broad moisture values with regional breakup."""
    latitude_band = 1.0 - abs(((y_ratio * 2.0) - 1.0) * 0.72)
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
    water_bias = 1.0 - (max(0.0, continentality) * 0.50)
    return clamp_unit(
        (macro_noise * MOISTURE_NOISE_WEIGHT)
        + (detail_noise * MOISTURE_DETAIL_WEIGHT)
        + (latitude_band * MOISTURE_LATITUDE_WEIGHT)
        + (water_bias * MOISTURE_WATER_BIAS_WEIGHT)
        + ((wrapped_value_noise(map_data.seed + 733, "moisture_warp_bias", x_ratio, y_ratio, 2.2) - 0.5) * MOISTURE_WARP_WEIGHT)
    )


def _build_temperature_value(map_data: MapData, x_ratio: float, y_ratio: float, ruggedness: float) -> float:
    """Return a latitude-led temperature field with some local breakup."""
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
    return clamp_unit(
        (equator_heat * TEMPERATURE_LATITUDE_WEIGHT)
        + (macro_noise * TEMPERATURE_NOISE_WEIGHT)
        + (detail_noise * TEMPERATURE_DETAIL_WEIGHT)
        + ((1.0 - ruggedness) * TEMPERATURE_RUGGEDNESS_WEIGHT)
    )


def _build_continent_regions(map_data: MapData, seam: SeamProfile) -> list[ContinentRegion]:
    """Return explicit bounded continent regions for continents mode."""
    continent_count = _continent_count(map_data)
    anchors = _select_continent_anchors(map_data, seam, continent_count)
    regions: list[ContinentRegion] = []
    for index, (center_x, center_y) in enumerate(anchors):
        radius_x = 0.09 + (0.025 * hash_unit_interval(map_data.seed + 111, "region_radius_x", index, 0))
        radius_y = 0.08 + (0.03 * hash_unit_interval(map_data.seed + 121, "region_radius_y", index, 1))
        strength = 0.78 + (0.14 * hash_unit_interval(map_data.seed + 131, "region_strength", index, 2))
        lobe_count = _range_count(
            map_data.seed + 141 + index,
            REGION_LOBES_MIN,
            REGION_LOBES_MAX,
            "region_lobe_count",
        )
        lobes: list[Lobe] = []
        for lobe_index in range(lobe_count):
            lobes.append(
                Lobe(
                    x=(center_x + ((hash_unit_interval(map_data.seed + 151, "region_dx", index, lobe_index) - 0.5) * radius_x * 1.2)) % 1.0,
                    y=min(0.86, max(0.14, center_y + ((hash_unit_interval(map_data.seed + 161, "region_dy", index, lobe_index) - 0.5) * radius_y * 1.2))),
                    radius_x=(radius_x * 0.45) + (radius_x * 0.20 * hash_unit_interval(map_data.seed + 171, "region_lobe_rx", index, lobe_index)),
                    radius_y=(radius_y * 0.45) + (radius_y * 0.24 * hash_unit_interval(map_data.seed + 181, "region_lobe_ry", index, lobe_index)),
                    strength=0.72 + (0.18 * hash_unit_interval(map_data.seed + 191, "region_lobe_strength", index, lobe_index)),
                )
            )
        regions.append(
            ContinentRegion(
                center_x=center_x,
                center_y=center_y,
                radius_x=radius_x,
                radius_y=radius_y,
                strength=strength,
                lobes=tuple(lobes),
            )
        )
    return regions


def _build_island_group_lobes(
    map_data: MapData,
    seam: SeamProfile,
    regions: list[ContinentRegion],
) -> list[Lobe]:
    """Return small island groups and short offshore chains."""
    count = _range_count(map_data.seed + 301, ISLAND_GROUP_MIN, ISLAND_GROUP_MAX, "island_count")
    lobes: list[Lobe] = []
    for index in range(count):
        parent = regions[index % len(regions)]
        side = -1.0 if hash_unit_interval(map_data.seed + 311, "island_side", index, 0) < 0.5 else 1.0
        anchor_x = _point_away_from_seam(
            seam,
            (parent.center_x + (side * parent.radius_x * (0.9 + (0.6 * hash_unit_interval(map_data.seed + 321, "island_offset", index, 1))))) % 1.0,
            min_gap=0.03,
        )
        anchor_y = min(
            0.90,
            max(
                0.10,
                parent.center_y + ((hash_unit_interval(map_data.seed + 331, "island_y", index, 2) - 0.5) * parent.radius_y * 1.8),
            ),
        )
        chain_lobes = _range_count(
            map_data.seed + 341 + index,
            1,
            3,
            "island_chain_lobes",
        )
        drift = 0.022 + (0.022 * hash_unit_interval(map_data.seed + 351, "island_drift", index, 3))
        for lobe_index in range(chain_lobes):
            lobes.append(
                Lobe(
                    x=(anchor_x + ((lobe_index - ((chain_lobes - 1) / 2.0)) * drift)) % 1.0,
                    y=min(0.92, max(0.08, anchor_y + ((lobe_index - ((chain_lobes - 1) / 2.0)) * drift * 0.6))),
                    radius_x=0.018 + (0.016 * hash_unit_interval(map_data.seed + 361, "island_radius_x", index, lobe_index)),
                    radius_y=0.018 + (0.016 * hash_unit_interval(map_data.seed + 371, "island_radius_y", index, lobe_index)),
                    strength=0.24 + (0.12 * hash_unit_interval(map_data.seed + 381, "island_strength", index, lobe_index)),
                )
            )
    return lobes


def _build_ruggedness_lobes(
    map_data: MapData,
    seam: SeamProfile,
    regions: list[ContinentRegion],
) -> list[Lobe]:
    """Return ruggedness clusters attached to continent interiors."""
    count = _range_count(map_data.seed + 501, RIDGE_CLUSTER_MIN, RIDGE_CLUSTER_MAX, "ridge_count")
    lobes: list[Lobe] = []
    for index in range(count):
        region = regions[index % len(regions)]
        x = _point_away_from_seam(
            seam,
            (region.center_x + ((hash_unit_interval(map_data.seed + 511, "ridge_dx", index, 0) - 0.5) * region.radius_x * 0.9)) % 1.0,
            min_gap=0.02,
        )
        y = min(
            0.88,
            max(
                0.12,
                region.center_y + ((hash_unit_interval(map_data.seed + 521, "ridge_dy", index, 1) - 0.5) * region.radius_y * 1.3),
            ),
        )
        lobes.append(
            Lobe(
                x=x,
                y=y,
                radius_x=0.028 + (0.028 * hash_unit_interval(map_data.seed + 531, "ridge_radius_x", index, 2)),
                radius_y=0.035 + (0.035 * hash_unit_interval(map_data.seed + 541, "ridge_radius_y", index, 3)),
                strength=0.62 + (0.24 * hash_unit_interval(map_data.seed + 551, "ridge_strength", index, 4)),
            )
        )
    return lobes


def _build_seam_profile(map_data: MapData) -> SeamProfile:
    """Return the preferred north-south ocean seam for display orientation."""
    center_x = 0.0
    width = SEAM_WIDTH_MIN + ((SEAM_WIDTH_MAX - SEAM_WIDTH_MIN) * hash_unit_interval(map_data.seed + 41, "seam_width", 0, 2))
    sway = 0.0
    tilt = 0.0
    return SeamProfile(center_x=center_x, width=width, sway=sway, tilt=tilt)


def _continent_region_field(regions: list[ContinentRegion], x_ratio: float, y_ratio: float) -> float:
    """Combine bounded continent regions into one normalized land field."""
    if not regions:
        return 0.0

    primary_region = min(
        regions,
        key=lambda region: _region_center_distance(region, x_ratio, y_ratio),
    )
    envelope = _elliptical_falloff(
        x_ratio,
        y_ratio,
        primary_region.center_x,
        primary_region.center_y,
        primary_region.radius_x,
        primary_region.radius_y,
    )
    if envelope <= 0.0:
        return 0.0

    local_shape = _lobe_field(list(primary_region.lobes), x_ratio, y_ratio)
    return clamp_unit(envelope * local_shape * primary_region.strength)


def _select_continent_anchors(
    map_data: MapData,
    seam: SeamProfile,
    count: int,
) -> list[tuple[float, float]]:
    """Select continent anchors in separated world sectors away from the seam."""
    min_gap = seam.width + 0.08
    usable_start = min_gap
    usable_end = 1.0 - (seam.width + 0.06)
    usable_span = max(usable_end - usable_start, 0.40)
    sector_width = usable_span / count
    band_order = _latitude_band_order(map_data, count)
    anchors: list[tuple[float, float]] = []

    for index in range(count):
        sector_start = usable_start + (sector_width * index)
        sector_end = sector_start + sector_width
        local_x = sector_start + (
            (0.18 + (0.64 * hash_unit_interval(map_data.seed + 181, "anchor_x", index, 0)))
            * sector_width
        )
        x = _point_away_from_seam(seam, min(local_x, sector_end - 0.01), min_gap=0.04)
        base_band = ANCHOR_LATITUDE_BANDS[band_order[index % len(band_order)]]
        y = base_band + ((hash_unit_interval(map_data.seed + 191, "anchor_y", index, 1) - 0.5) * 0.12)
        anchors.append((x, min(0.78, max(0.22, y))))

    return anchors


def _continent_count(map_data: MapData) -> int:
    """Return a weighted deterministic count where two large continents are most common."""
    roll = hash_unit_interval(map_data.seed + 101, "main_count_roll", 0, 0)
    if roll < 0.50:
        return 2
    if roll < 0.82:
        return 3
    return 4


def _latitude_band_order(map_data: MapData, count: int) -> list[int]:
    """Return a deterministic ordering of latitude bands for continent anchors."""
    if count == 2:
        return [1, 2]
    if count == 3:
        return [1, 2, 0 if hash_unit_interval(map_data.seed + 171, "band_pick", 0, 0) < 0.5 else 3]
    if hash_unit_interval(map_data.seed + 171, "band_flip", 0, 1) < 0.5:
        return [0, 1, 2, 3]
    return [3, 2, 1, 0]


def _lobe_field(lobes: list[Lobe], x_ratio: float, y_ratio: float) -> float:
    """Combine several broad lobes into one normalized field."""
    influence = 0.0
    for lobe in lobes:
        x_distance = _wrapped_distance(x_ratio, lobe.x) / lobe.radius_x
        y_distance = (y_ratio - lobe.y) / lobe.radius_y
        distance_squared = (x_distance * x_distance) + (y_distance * y_distance)
        if distance_squared >= 1.0:
            continue
        influence += (1.0 - distance_squared) ** 2 * lobe.strength
    return clamp_unit(influence)


def _elliptical_falloff(
    x_ratio: float,
    y_ratio: float,
    center_x: float,
    center_y: float,
    radius_x: float,
    radius_y: float,
) -> float:
    """Return a bounded elliptical falloff used to keep continents discrete."""
    x_distance = _wrapped_distance(x_ratio, center_x) / radius_x
    y_distance = (y_ratio - center_y) / radius_y
    distance_squared = (x_distance * x_distance) + (y_distance * y_distance)
    if distance_squared >= 1.0:
        return 0.0
    value = 1.0 - distance_squared
    return value * value


def _seam_field(seam: SeamProfile, x_ratio: float, y_ratio: float) -> float:
    """Return the preferred ocean seam influence for one map position."""
    seam_center = (
        seam.center_x
        + ((y_ratio - 0.5) * seam.tilt)
        + ((0.5 - abs(y_ratio - 0.5)) * seam.sway)
    ) % 1.0
    return _band_falloff_wrapped(x_ratio, seam_center, seam.width)


def _range_count(seed: int, minimum: int, maximum: int, label: str) -> int:
    """Return a deterministic integer count in an inclusive range."""
    span = maximum - minimum + 1
    value = int(hash_unit_interval(seed, label, 0, 0) * span)
    return minimum + min(span - 1, value)


def _point_away_from_seam(seam: SeamProfile, x_value: float, min_gap: float) -> float:
    """Shift an x position away from the seam corridor if needed."""
    if _wrapped_distance(x_value, seam.center_x) >= (seam.width + min_gap):
        return x_value
    direction = 1.0 if ((x_value - seam.center_x) % 1.0) < 0.5 else -1.0
    return (seam.center_x + (direction * (seam.width + min_gap))) % 1.0


def _wrapped_distance(a: float, b: float) -> float:
    """Return wrapped x-axis distance on the 0..1 world strip."""
    raw = abs(a - b)
    return min(raw, 1.0 - raw)


def _region_center_distance(region: ContinentRegion, x_ratio: float, y_ratio: float) -> float:
    """Return wrapped distance from a sample point to a region center."""
    return math.hypot(_wrapped_distance(x_ratio, region.center_x), abs(y_ratio - region.center_y))


def _band_falloff_wrapped(value: float, center: float, half_width: float) -> float:
    """Return a smooth wrapped band influence around a center line."""
    distance = _wrapped_distance(value, center)
    if distance >= half_width:
        return 0.0
    normalized = 1.0 - (distance / half_width)
    return normalized * normalized * (3.0 - (2.0 * normalized))


def _warp_coords(map_data: MapData, x_ratio: float, y_ratio: float, label: str) -> tuple[float, float]:
    """Warp world-space sample coordinates to reduce large-scale directional artifacts."""
    warp_x = wrapped_value_noise(map_data.seed + 901, f"{label}_warp_x", x_ratio, y_ratio, 2.0) - 0.5
    warp_y = wrapped_value_noise(map_data.seed + 911, f"{label}_warp_y", x_ratio, y_ratio, 2.4) - 0.5
    warped_x = (x_ratio + (warp_x * 0.12)) % 1.0
    warped_y = max(0.0, min(1.0, y_ratio + (warp_y * 0.10)))
    return warped_x, warped_y


def _tile_world_ratios(map_data: MapData, display_col: int, display_row: int) -> tuple[float, float]:
    """Return cylindrical world-space ratios derived from actual hex-center positions."""
    center_x = SQRT_3 * (display_col + (0.5 if display_row & 1 else 0.0))
    center_y = 1.5 * display_row
    wrap_width = SQRT_3 * map_data.width
    max_height = max(1.5 * max(map_data.height - 1, 1), 1.0)
    x_ratio = (center_x % wrap_width) / wrap_width
    y_ratio = center_y / max_height
    return x_ratio, max(0.0, min(1.0, y_ratio))
