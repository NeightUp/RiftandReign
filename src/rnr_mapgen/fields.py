"""Deterministic scalar-field generation for the map foundation."""

from __future__ import annotations

import math
from hashlib import blake2b

from rnr_mapgen.hex import HexCoord
from rnr_mapgen.types import MapData


FieldName = str
_FIELD_NAMES: tuple[FieldName, ...] = ("elevation", "moisture", "temperature")

CONTINENT_NOISE_SCALE = 2.8
CONTINENT_DETAIL_SCALE = 5.6
RIDGE_NOISE_SCALE = 8.4
MOISTURE_NOISE_SCALE = 4.2
TEMPERATURE_NOISE_SCALE = 3.6
EDGE_OCEAN_MARGIN = 0.10
EDGE_OCEAN_WEIGHT = 0.08
OCEAN_CHANNEL_THRESHOLD = 0.48
OCEAN_CHANNEL_WEIGHT = 0.24
OCEAN_CENTER_WEIGHT = 0.22
RIFT_CHANNEL_WEIGHT = 0.18
CONTINENT_CENTER_WEIGHT = 0.36
SUBCONTINENT_CENTER_WEIGHT = 0.14
CONTINENT_NOISE_WEIGHT = 0.26
CONTINENT_DETAIL_WEIGHT = 0.12
RIDGE_WEIGHT = 0.10
COASTAL_BREAKUP_WEIGHT = 0.08
BASE_ELEVATION_OFFSET = 0.08
TEMPERATURE_LATITUDE_WEIGHT = 0.72
TEMPERATURE_NOISE_WEIGHT = 0.18
TEMPERATURE_LONGITUDE_WEIGHT = 0.10
MOISTURE_NOISE_WEIGHT = 0.56
MOISTURE_BAND_WEIGHT = 0.24
MOISTURE_SWIRL_WEIGHT = 0.20


def generate_scalar_fields(map_data: MapData) -> MapData:
    """Populate deterministic scalar values on every tile."""
    raw_values = {
        field_name: _build_raw_field(map_data, field_name) for field_name in _FIELD_NAMES
    }
    smoothed_values = {
        field_name: _smooth_field(map_data, field_values)
        for field_name, field_values in raw_values.items()
    }

    for coord, tile in map_data.tiles.items():
        tile.elevation = smoothed_values["elevation"][coord]
        tile.moisture = smoothed_values["moisture"][coord]
        tile.temperature = smoothed_values["temperature"][coord]

    return map_data


def _build_raw_field(map_data: MapData, field_name: FieldName) -> dict[HexCoord, float]:
    """Build the initial unsmoothed scalar field for one channel."""
    values: dict[HexCoord, float] = {}
    continent_centers = _build_continent_centers(map_data)
    subcontinent_centers = _build_subcontinent_centers(map_data)
    ocean_centers = _build_ocean_centers(map_data)

    for coord, tile in map_data.tiles.items():
        x_ratio = _axis_ratio(tile.display_col, map_data.width)
        y_ratio = _axis_ratio(tile.display_row, map_data.height)

        if field_name == "elevation":
            values[coord] = _build_elevation_value(
                map_data=map_data,
                coord=coord,
                x_ratio=x_ratio,
                y_ratio=y_ratio,
                continent_centers=continent_centers,
                subcontinent_centers=subcontinent_centers,
                ocean_centers=ocean_centers,
            )
        elif field_name == "moisture":
            values[coord] = _build_moisture_value(
                map_data=map_data,
                coord=coord,
                x_ratio=x_ratio,
                y_ratio=y_ratio,
            )
        else:
            values[coord] = _build_temperature_value(
                map_data=map_data,
                coord=coord,
                x_ratio=x_ratio,
                y_ratio=y_ratio,
            )

    return values


def _build_elevation_value(
    map_data: MapData,
    coord: HexCoord,
    x_ratio: float,
    y_ratio: float,
    continent_centers: list[tuple[float, float, float, float, float]],
    subcontinent_centers: list[tuple[float, float, float, float, float]],
    ocean_centers: list[tuple[float, float, float, float, float]],
) -> float:
    """Build a broad continent-friendly elevation field."""
    continent_noise = _value_noise(map_data.seed + 101, "continent", x_ratio, y_ratio, CONTINENT_NOISE_SCALE)
    detail_noise = _value_noise(map_data.seed + 151, "detail", x_ratio, y_ratio, CONTINENT_DETAIL_SCALE)
    ridge_noise = 1.0 - abs((_value_noise(map_data.seed + 211, "ridge", x_ratio, y_ratio, RIDGE_NOISE_SCALE) * 2.0) - 1.0)
    ocean_channel_noise = _value_noise(map_data.seed + 271, "ocean", x_ratio, y_ratio, 2.2)
    coastal_breakup_noise = _value_noise(map_data.seed + 311, "coast_breakup", x_ratio, y_ratio, 7.4)
    ocean_channel = _clamp_unit((OCEAN_CHANNEL_THRESHOLD - ocean_channel_noise) / OCEAN_CHANNEL_THRESHOLD)
    center_influence = _continent_center_influence(
        map_data=map_data,
        display_col=map_data.tiles[coord].display_col,
        display_row=map_data.tiles[coord].display_row,
        centers=continent_centers,
    )
    subcontinent_influence = _continent_center_influence(
        map_data=map_data,
        display_col=map_data.tiles[coord].display_col,
        display_row=map_data.tiles[coord].display_row,
        centers=subcontinent_centers,
    )
    ocean_center_influence = _continent_center_influence(
        map_data=map_data,
        display_col=map_data.tiles[coord].display_col,
        display_row=map_data.tiles[coord].display_row,
        centers=ocean_centers,
    )
    edge_ocean = _edge_ocean_falloff(x_ratio, y_ratio)
    rift_channel = _rift_channel_influence(map_data, x_ratio, y_ratio)

    raw_value = (
        BASE_ELEVATION_OFFSET
        + (CONTINENT_CENTER_WEIGHT * center_influence)
        + (SUBCONTINENT_CENTER_WEIGHT * subcontinent_influence)
        + (CONTINENT_NOISE_WEIGHT * continent_noise)
        + (CONTINENT_DETAIL_WEIGHT * detail_noise)
        + (RIDGE_WEIGHT * ridge_noise)
        + (COASTAL_BREAKUP_WEIGHT * (coastal_breakup_noise - 0.5))
        - (OCEAN_CHANNEL_WEIGHT * ocean_channel)
        - (OCEAN_CENTER_WEIGHT * ocean_center_influence)
        - (RIFT_CHANNEL_WEIGHT * rift_channel)
        - (EDGE_OCEAN_WEIGHT * edge_ocean)
    )
    return _clamp_unit(raw_value)


def _build_moisture_value(
    map_data: MapData,
    coord: HexCoord,
    x_ratio: float,
    y_ratio: float,
) -> float:
    """Build a broad moisture field with large-scale variation."""
    noise = _value_noise(map_data.seed + 401, "moisture", x_ratio, y_ratio, MOISTURE_NOISE_SCALE)
    banding = _value_noise(map_data.seed + 431, "moisture_band", x_ratio, y_ratio, 2.4)
    swirl = _value_noise(map_data.seed + 461, "moisture_swirl", y_ratio, x_ratio, 3.0)
    raw_value = (
        (MOISTURE_NOISE_WEIGHT * noise)
        + (MOISTURE_BAND_WEIGHT * banding)
        + (MOISTURE_SWIRL_WEIGHT * swirl)
    )
    return _clamp_unit(raw_value)


def _build_temperature_value(
    map_data: MapData,
    coord: HexCoord,
    x_ratio: float,
    y_ratio: float,
) -> float:
    """Build a latitude-driven temperature field for a world-strip layout."""
    latitude_distance = abs((y_ratio * 2.0) - 1.0)
    equator_heat = 1.0 - latitude_distance
    temperature_noise = _value_noise(
        map_data.seed + 501,
        "temperature",
        x_ratio,
        y_ratio,
        TEMPERATURE_NOISE_SCALE,
    )
    longitude_variation = _value_noise(
        map_data.seed + 541,
        "temperature_longitude",
        x_ratio,
        y_ratio,
        2.0,
    )
    raw_value = (
        (TEMPERATURE_LATITUDE_WEIGHT * equator_heat)
        + (TEMPERATURE_NOISE_WEIGHT * temperature_noise)
        + (TEMPERATURE_LONGITUDE_WEIGHT * longitude_variation)
    )
    return _clamp_unit(raw_value)


def _smooth_field(
    map_data: MapData, field_values: dict[HexCoord, float]
) -> dict[HexCoord, float]:
    """Apply one local neighbor-influence pass to reduce isolated spikes."""
    smoothed: dict[HexCoord, float] = {}

    for coord in map_data.tiles:
        neighbors = [
            neighbor for neighbor in coord.list_neighbors() if neighbor in map_data.tiles
        ]
        if not neighbors:
            smoothed[coord] = field_values[coord]
            continue

        neighbor_average = sum(field_values[neighbor] for neighbor in neighbors) / len(
            neighbors
        )
        smoothed[coord] = _clamp_unit((0.72 * field_values[coord]) + (0.28 * neighbor_average))

    return smoothed


def _build_continent_centers(map_data: MapData) -> list[tuple[float, float, float, float, float]]:
    """Return deterministic broad continent-center descriptors."""
    center_count = max(3, min(6, (map_data.width * map_data.height) // 140 + 2))
    centers: list[tuple[float, float, float, float, float]] = []

    for index in range(center_count):
        x = _hash_unit_interval(map_data.seed + 601 + index, "center_x", HexCoord(index, 0))
        y = _hash_unit_interval(map_data.seed + 641 + index, "center_y", HexCoord(index, 1))
        radius_x = 0.18 + (
            0.14
            * _hash_unit_interval(map_data.seed + 681 + index, "radius_x", HexCoord(index, 2))
        )
        radius_y = 0.20 + (
            0.16
            * _hash_unit_interval(map_data.seed + 721 + index, "radius_y", HexCoord(index, 3))
        )
        strength = 0.72 + (
            0.24
            * _hash_unit_interval(map_data.seed + 761 + index, "strength", HexCoord(index, 4))
        )
        centers.append((x, y, radius_x, radius_y, strength))

    return centers


def _build_ocean_centers(map_data: MapData) -> list[tuple[float, float, float, float, float]]:
    """Return deterministic broad ocean-break descriptors."""
    center_count = max(2, min(4, (map_data.width * map_data.height) // 220 + 1))
    centers: list[tuple[float, float, float, float, float]] = []

    for index in range(center_count):
        x = _hash_unit_interval(map_data.seed + 801 + index, "ocean_x", HexCoord(index, 0))
        y = _hash_unit_interval(map_data.seed + 841 + index, "ocean_y", HexCoord(index, 1))
        radius_x = 0.12 + (
            0.10
            * _hash_unit_interval(map_data.seed + 881 + index, "ocean_radius_x", HexCoord(index, 2))
        )
        radius_y = 0.14 + (
            0.12
            * _hash_unit_interval(map_data.seed + 921 + index, "ocean_radius_y", HexCoord(index, 3))
        )
        strength = 0.74 + (
            0.22
            * _hash_unit_interval(map_data.seed + 961 + index, "ocean_strength", HexCoord(index, 4))
        )
        centers.append((x, y, radius_x, radius_y, strength))

    return centers


def _build_subcontinent_centers(map_data: MapData) -> list[tuple[float, float, float, float, float]]:
    """Return deterministic smaller secondary landmass descriptors."""
    center_count = max(2, min(6, (map_data.width * map_data.height) // 180 + 1))
    centers: list[tuple[float, float, float, float, float]] = []

    for index in range(center_count):
        x = _hash_unit_interval(map_data.seed + 1061 + index, "subcontinent_x", HexCoord(index, 0))
        y = _hash_unit_interval(map_data.seed + 1101 + index, "subcontinent_y", HexCoord(index, 1))
        radius_x = 0.10 + (
            0.08
            * _hash_unit_interval(map_data.seed + 1141 + index, "subcontinent_radius_x", HexCoord(index, 2))
        )
        radius_y = 0.10 + (
            0.10
            * _hash_unit_interval(map_data.seed + 1181 + index, "subcontinent_radius_y", HexCoord(index, 3))
        )
        strength = 0.48 + (
            0.18
            * _hash_unit_interval(map_data.seed + 1221 + index, "subcontinent_strength", HexCoord(index, 4))
        )
        centers.append((x, y, radius_x, radius_y, strength))

    return centers


def _continent_center_influence(
    map_data: MapData,
    display_col: int,
    display_row: int,
    centers: list[tuple[float, float, float, float, float]],
) -> float:
    """Return the combined influence from several broad continent centers."""
    x_ratio = _axis_ratio(display_col, map_data.width)
    y_ratio = _axis_ratio(display_row, map_data.height)
    influence = 0.0

    for center_x, center_y, radius_x, radius_y, strength in centers:
        x_distance = (x_ratio - center_x) / radius_x
        y_distance = (y_ratio - center_y) / radius_y
        distance_squared = (x_distance * x_distance) + (y_distance * y_distance)
        if distance_squared >= 1.0:
            continue

        falloff = (1.0 - distance_squared) ** 2
        influence += falloff * strength

    return _clamp_unit(influence)


def _edge_ocean_falloff(x_ratio: float, y_ratio: float) -> float:
    """Return a mild preference for water near the outermost borders."""
    min_edge_distance = min(x_ratio, 1.0 - x_ratio, y_ratio, 1.0 - y_ratio)
    if min_edge_distance >= EDGE_OCEAN_MARGIN:
        return 0.0

    return 1.0 - (min_edge_distance / EDGE_OCEAN_MARGIN)


def _rift_channel_influence(map_data: MapData, x_ratio: float, y_ratio: float) -> float:
    """Return deterministic broad ocean-corridor influence."""
    vertical_center = 0.25 + (
        0.50
        * _hash_unit_interval(map_data.seed + 1001, "rift_vertical", HexCoord(0, 0))
    )
    vertical_width = 0.06 + (
        0.06
        * _hash_unit_interval(map_data.seed + 1011, "rift_vertical_width", HexCoord(0, 1))
    )
    horizontal_center = 0.28 + (
        0.44
        * _hash_unit_interval(map_data.seed + 1021, "rift_horizontal", HexCoord(0, 2))
    )
    horizontal_width = 0.05 + (
        0.05
        * _hash_unit_interval(map_data.seed + 1031, "rift_horizontal_width", HexCoord(0, 3))
    )
    diagonal_bias = 0.20 + (
        0.25
        * _hash_unit_interval(map_data.seed + 1041, "rift_diagonal", HexCoord(0, 4))
    )

    vertical = _band_falloff(x_ratio, vertical_center, vertical_width)
    horizontal = _band_falloff(y_ratio, horizontal_center, horizontal_width)
    diagonal = _band_falloff(x_ratio + (diagonal_bias * y_ratio), 0.55, 0.08)
    return _clamp_unit(max(vertical, horizontal * 0.9, diagonal * 0.75))


def _value_noise(seed: int, field_name: str, x_ratio: float, y_ratio: float, scale: float) -> float:
    """Return smooth deterministic 2D value noise in the 0.0..1.0 range."""
    x = x_ratio * scale
    y = y_ratio * scale
    x0 = math.floor(x)
    y0 = math.floor(y)
    x1 = x0 + 1
    y1 = y0 + 1
    tx = x - x0
    ty = y - y0

    v00 = _hash_grid_value(seed, field_name, x0, y0)
    v10 = _hash_grid_value(seed, field_name, x1, y0)
    v01 = _hash_grid_value(seed, field_name, x0, y1)
    v11 = _hash_grid_value(seed, field_name, x1, y1)

    sx = _smoothstep(tx)
    sy = _smoothstep(ty)
    i0 = _lerp(v00, v10, sx)
    i1 = _lerp(v01, v11, sx)
    return _lerp(i0, i1, sy)


def _hash_grid_value(seed: int, field_name: str, grid_x: int, grid_y: int) -> float:
    """Return a deterministic pseudo-random grid value in the 0.0..1.0 range."""
    payload = f"{seed}:{field_name}:{grid_x}:{grid_y}".encode("ascii")
    digest = blake2b(payload, digest_size=8).digest()
    numerator = int.from_bytes(digest, byteorder="big")
    return numerator / ((1 << 64) - 1)


def _hash_unit_interval(seed: int, field_name: str, coord: HexCoord) -> float:
    """Return a deterministic pseudo-random value in the range 0.0..1.0."""
    payload = f"{seed}:{field_name}:{coord.q}:{coord.r}".encode("ascii")
    digest = blake2b(payload, digest_size=8).digest()
    numerator = int.from_bytes(digest, byteorder="big")
    return numerator / ((1 << 64) - 1)


def _axis_ratio(index: int, size: int) -> float:
    """Convert a board index into a stable 0.0..1.0 ratio."""
    if size <= 1:
        return 0.5
    return index / (size - 1)


def _smoothstep(value: float) -> float:
    """Return a smooth interpolation factor in the 0.0..1.0 range."""
    return value * value * (3.0 - (2.0 * value))


def _band_falloff(value: float, center: float, half_width: float) -> float:
    """Return a smooth 0.0..1.0 band falloff around a center line."""
    distance = abs(value - center)
    if distance >= half_width:
        return 0.0
    return _smoothstep(1.0 - (distance / half_width))


def _lerp(start: float, end: float, factor: float) -> float:
    """Linearly interpolate between two values."""
    return start + ((end - start) * factor)


def _clamp_unit(value: float) -> float:
    """Clamp a scalar value into the 0.0..1.0 range."""
    return max(0.0, min(1.0, value))
