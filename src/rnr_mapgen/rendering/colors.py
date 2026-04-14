"""Current flat map colors for rendering."""

from __future__ import annotations

from typing import TypeAlias

from rnr_mapgen.domain.models import TileData


Color: TypeAlias = tuple[int, int, int]

BACKGROUND_COLOR: Color = (18, 20, 26)
GRID_LINE_COLOR: Color = (32, 36, 44)
HUD_BACKGROUND_COLOR: Color = (9, 11, 16)
HUD_TEXT_COLOR: Color = (234, 236, 242)
DEEP_WATER_COLOR: Color = (28, 70, 138)
SHALLOW_WATER_COLOR: Color = (44, 98, 173)
INLAND_WATER_COLOR: Color = (74, 126, 190)
RIVER_COLOR: Color = (132, 199, 255)

BIOME_COLORS: dict[str, Color] = {
    "plains": (134, 176, 90),
    "forest": (52, 122, 68),
    "desert": (210, 186, 108),
    "tundra": (176, 194, 204),
    "hills": (146, 118, 76),
    "mountains": (125, 127, 133),
}

FALLBACK_LAND_COLOR: Color = (168, 168, 168)


def get_tile_fill_color(tile: TileData) -> Color:
    """Return the current flat fill color for a tile."""
    if tile.is_water:
        if tile.water_class == "deep_ocean":
            return DEEP_WATER_COLOR
        if tile.water_class in {"lake", "inland_sea"}:
            return INLAND_WATER_COLOR
        return SHALLOW_WATER_COLOR
    if tile.biome is None:
        return FALLBACK_LAND_COLOR
    return BIOME_COLORS.get(tile.biome, FALLBACK_LAND_COLOR)
