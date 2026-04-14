"""Deterministic first-pass biome classification for land tiles."""

from __future__ import annotations

from collections import Counter

from rnr_mapgen.board import display_to_axial, iter_neighbor_coords
from rnr_mapgen.types import MapData


MOUNTAIN_ELEVATION_THRESHOLD = 0.68
HILL_ELEVATION_THRESHOLD = 0.49
TUNDRA_TEMPERATURE_THRESHOLD = 0.24
DESERT_MOISTURE_THRESHOLD = 0.33
DESERT_TEMPERATURE_THRESHOLD = 0.57
FOREST_MOISTURE_THRESHOLD = 0.56
RIVER_FOREST_BONUS = 0.06
RUGGED_MOUNTAIN_THRESHOLD = 0.62
RUGGED_HILL_THRESHOLD = 0.42
FOREST_RUGGEDNESS_PENALTY = 0.06
COASTAL_MOISTURE_BONUS = 0.18
INLAND_DRYNESS_PENALTY = 0.18
ELEVATION_COOLING_WEIGHT = 0.14
NEIGHBOR_RUGGEDNESS_SHADOW_WEIGHT = 0.10

BIOME_PREVIEW_CHARS: dict[str, str] = {
    "plains": "p",
    "forest": "f",
    "desert": "d",
    "tundra": "t",
    "hills": "h",
    "mountains": "m",
}


def classify_biomes(map_data: MapData) -> MapData:
    """Assign first-pass biome labels to all land tiles."""
    distance_to_water = _distance_to_water(map_data)

    for tile in map_data.tiles.values():
        if tile.is_water:
            tile.biome = None
            tile.terrain_class = tile.water_class or "water"
            continue

        tile.biome = _classify_land_biome(map_data, tile, distance_to_water)
        tile.terrain_class = tile.biome

    return map_data


def render_ascii_biomes(map_data: MapData) -> str:
    """Render a compact ASCII preview of land, rivers, and biome families."""
    preview_width = min(map_data.width, map_data.config.preview_width)
    preview_height = min(map_data.height, map_data.config.preview_height)
    lines: list[str] = []

    for display_row in range(preview_height):
        chars: list[str] = []
        for display_col in range(preview_width):
            tile = map_data.tiles[display_to_axial(display_col, display_row)]
            if tile.is_water:
                chars.append(".")
            elif tile.has_river:
                chars.append("~")
            else:
                chars.append(BIOME_PREVIEW_CHARS.get(tile.biome or "", "?"))

        indent = " " if display_row % 2 else ""
        lines.append(f"{indent}{''.join(chars)}")

    return "\n".join(lines)


def summarize_biomes(map_data: MapData) -> str:
    """Return a concise terrain, river, and biome summary for CLI output."""
    elevation_values = [tile.elevation for tile in map_data.tiles.values()]
    moisture_values = [tile.moisture for tile in map_data.tiles.values()]
    temperature_values = [tile.temperature for tile in map_data.tiles.values()]
    land_tiles = sum(1 for tile in map_data.tiles.values() if not tile.is_water)
    water_tiles = map_data.tile_count - land_tiles
    river_tiles = sum(1 for tile in map_data.tiles.values() if tile.has_river)
    max_river_strength = max(
        (tile.river_strength for tile in map_data.tiles.values()),
        default=0.0,
    )
    land_percentage = (land_tiles / map_data.tile_count) * 100.0
    biome_counts = Counter(
        tile.biome for tile in map_data.tiles.values() if not tile.is_water and tile.biome
    )

    biome_lines = [
        f"  {biome}: {count}"
        for biome, count in sorted(biome_counts.items())
    ]

    return "\n".join(
        [
            "RiftandReign first-pass biome groundwork.",
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
            "Biome counts:",
            *biome_lines,
            (
                "ASCII preview policy: top-left crop "
                f"up to {map_data.config.preview_width}x{map_data.config.preview_height}."
            ),
            "ASCII biome preview (. water, ~ river, p plains, f forest, d desert, t tundra, h hills, m mountains):",
            render_ascii_biomes(map_data),
            "Start validation is not implemented yet.",
        ]
    )


def _classify_land_biome(map_data: MapData, tile, distance_to_water: dict) -> str:
    """Return the first-pass biome label for one land tile."""
    if (
        tile.elevation >= MOUNTAIN_ELEVATION_THRESHOLD
        and tile.ruggedness >= RUGGED_MOUNTAIN_THRESHOLD
    ):
        return "mountains"

    if (
        tile.elevation >= HILL_ELEVATION_THRESHOLD
        or tile.ruggedness >= RUGGED_HILL_THRESHOLD
    ):
        return "hills"

    coastal_factor = max(0.0, 1.0 - (distance_to_water[tile.coord] / 6.0))
    inland_factor = min(distance_to_water[tile.coord] / 8.0, 1.0)
    neighbor_ruggedness = _neighbor_ruggedness(map_data, tile.coord)
    effective_temperature = tile.temperature - (tile.elevation * ELEVATION_COOLING_WEIGHT)
    effective_moisture = (
        tile.moisture
        + (coastal_factor * COASTAL_MOISTURE_BONUS)
        + (RIVER_FOREST_BONUS if tile.has_river else 0.0)
        - (inland_factor * INLAND_DRYNESS_PENALTY)
        - (neighbor_ruggedness * NEIGHBOR_RUGGEDNESS_SHADOW_WEIGHT)
        - (tile.ruggedness * FOREST_RUGGEDNESS_PENALTY)
    )

    if effective_temperature <= TUNDRA_TEMPERATURE_THRESHOLD:
        return "tundra"

    if (
        effective_moisture <= DESERT_MOISTURE_THRESHOLD
        and effective_temperature >= DESERT_TEMPERATURE_THRESHOLD
        and distance_to_water[tile.coord] >= 2
    ):
        return "desert"

    if effective_moisture >= FOREST_MOISTURE_THRESHOLD:
        return "forest"

    return "plains"


def _distance_to_water(map_data: MapData) -> dict:
    """Return tile distance from land to nearest water."""
    from collections import deque

    distances: dict = {}
    frontier: deque = deque()

    for coord, tile in map_data.tiles.items():
        if tile.is_water:
            distances[coord] = 0
            frontier.append(coord)

    while frontier:
        current = frontier.popleft()
        for neighbor in iter_neighbor_coords(map_data, current):
            if neighbor in distances:
                continue
            distances[neighbor] = distances[current] + 1
            frontier.append(neighbor)

    for coord in map_data.tiles:
        distances.setdefault(coord, 0)

    return distances


def _neighbor_ruggedness(map_data: MapData, coord) -> float:
    """Return mean neighboring ruggedness around a tile."""
    neighbors = iter_neighbor_coords(map_data, coord)
    if not neighbors:
        return 0.0
    return sum(map_data.tiles[neighbor].ruggedness for neighbor in neighbors) / len(neighbors)
