"""Deterministic first-pass biome classification for land tiles."""

from __future__ import annotations

from collections import Counter

from rnr_mapgen.hex import HexCoord
from rnr_mapgen.types import MapData


MOUNTAIN_ELEVATION_THRESHOLD = 0.68
HILL_ELEVATION_THRESHOLD = 0.56
TUNDRA_TEMPERATURE_THRESHOLD = 0.28
DESERT_MOISTURE_THRESHOLD = 0.22
DESERT_TEMPERATURE_THRESHOLD = 0.45
FOREST_MOISTURE_THRESHOLD = 0.58
RIVER_FOREST_BONUS = 0.08

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
    for tile in map_data.tiles.values():
        if tile.is_water:
            tile.biome = None
            continue

        tile.biome = _classify_land_biome(tile)

    return map_data


def render_ascii_biomes(map_data: MapData) -> str:
    """Render a compact ASCII preview of land, rivers, and biome families."""
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
                chars.append(BIOME_PREVIEW_CHARS.get(tile.biome or "", "?"))

        indent = " " if r % 2 else ""
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
            "ASCII biome preview (. water, ~ river, p plains, f forest, d desert, t tundra, h hills, m mountains):",
            render_ascii_biomes(map_data),
            "Start validation is not implemented yet.",
        ]
    )


def _classify_land_biome(tile) -> str:
    """Return the first-pass biome label for one land tile."""
    if tile.elevation >= MOUNTAIN_ELEVATION_THRESHOLD:
        return "mountains"

    if tile.elevation >= HILL_ELEVATION_THRESHOLD:
        return "hills"

    if tile.temperature <= TUNDRA_TEMPERATURE_THRESHOLD:
        return "tundra"

    if (
        tile.moisture <= DESERT_MOISTURE_THRESHOLD
        and tile.temperature >= DESERT_TEMPERATURE_THRESHOLD
    ):
        return "desert"

    effective_moisture = tile.moisture + (RIVER_FOREST_BONUS if tile.has_river else 0.0)
    if effective_moisture >= FOREST_MOISTURE_THRESHOLD:
        return "forest"

    return "plains"
