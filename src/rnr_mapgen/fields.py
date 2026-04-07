"""Deterministic scalar-field generation for the map foundation."""

from __future__ import annotations

from hashlib import blake2b

from rnr_mapgen.hex import HexCoord
from rnr_mapgen.types import MapData


FieldName = str
_FIELD_NAMES: tuple[FieldName, ...] = ("elevation", "moisture", "temperature")


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


def summarize_scalar_fields(map_data: MapData, sample_size: int = 4) -> str:
    """Return a compact CLI summary of scalar-field output."""
    elevation_values = [tile.elevation for tile in map_data.tiles.values()]
    moisture_values = [tile.moisture for tile in map_data.tiles.values()]
    temperature_values = [tile.temperature for tile in map_data.tiles.values()]
    sample_tiles = list(map_data.tiles.values())[:sample_size]

    sample_lines = [
        (
            f"  ({tile.coord.q},{tile.coord.r}) "
            f"e={tile.elevation:.3f} "
            f"m={tile.moisture:.3f} "
            f"t={tile.temperature:.3f}"
        )
        for tile in sample_tiles
    ]

    return "\n".join(
        [
            "RiftandReign scalar-field groundwork only.",
            f"Dimensions: {map_data.width}x{map_data.height}",
            f"Seed: {map_data.seed}",
            f"Total tiles: {map_data.tile_count}",
            (
                "Elevation range: "
                f"{min(elevation_values):.3f}..{max(elevation_values):.3f}"
            ),
            (
                "Moisture range: "
                f"{min(moisture_values):.3f}..{max(moisture_values):.3f}"
            ),
            (
                "Temperature range: "
                f"{min(temperature_values):.3f}..{max(temperature_values):.3f}"
            ),
            "Sample tiles:",
            *sample_lines,
            "Terrain classification, hydrology, and biomes are not implemented yet.",
        ]
    )


def _build_raw_field(map_data: MapData, field_name: FieldName) -> dict[HexCoord, float]:
    """Build the initial unsmoothed scalar field for one channel."""
    values: dict[HexCoord, float] = {}

    for coord in map_data.tiles:
        q_ratio = _axis_ratio(coord.q, map_data.width)
        r_ratio = _axis_ratio(coord.r, map_data.height)
        center_bias = _center_bias(q_ratio, r_ratio)
        base_noise = _hash_unit_interval(map_data.seed, field_name, coord)

        if field_name == "elevation":
            ridge_noise = _hash_unit_interval(map_data.seed + 17, "ridge", coord)
            raw_value = (
                0.50 * base_noise
                + 0.35 * center_bias
                + 0.15 * ridge_noise
            )
        elif field_name == "moisture":
            north_south_band = 1.0 - abs((r_ratio * 2.0) - 1.0)
            raw_value = (
                0.55 * base_noise
                + 0.25 * north_south_band
                + 0.20 * (1.0 - q_ratio)
            )
        else:
            north_warmth = 1.0 - r_ratio
            east_west_balance = 1.0 - abs((q_ratio * 2.0) - 1.0)
            raw_value = (
                0.55 * north_warmth
                + 0.20 * east_west_balance
                + 0.25 * base_noise
            )

        values[coord] = _clamp_unit(raw_value)

    return values


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
        smoothed[coord] = _clamp_unit((0.70 * field_values[coord]) + (0.30 * neighbor_average))

    return smoothed


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


def _center_bias(q_ratio: float, r_ratio: float) -> float:
    """Return a simple center-emphasis value in the range 0.0..1.0."""
    q_distance = abs((q_ratio * 2.0) - 1.0)
    r_distance = abs((r_ratio * 2.0) - 1.0)
    return _clamp_unit(1.0 - max(q_distance, r_distance))


def _clamp_unit(value: float) -> float:
    """Clamp a scalar value into the 0.0..1.0 range."""
    return max(0.0, min(1.0, value))
