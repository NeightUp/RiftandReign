"""Compatibility exports for current rendering colors."""

from rnr_mapgen.rendering.colors import (
    BACKGROUND_COLOR,
    BIOME_COLORS,
    DEEP_WATER_COLOR,
    FALLBACK_LAND_COLOR,
    GRID_LINE_COLOR,
    HUD_BACKGROUND_COLOR,
    HUD_TEXT_COLOR,
    INLAND_WATER_COLOR,
    RIVER_COLOR,
    SHALLOW_WATER_COLOR,
    get_tile_fill_color,
)

WATER_COLOR = SHALLOW_WATER_COLOR

__all__ = [
    "BACKGROUND_COLOR",
    "BIOME_COLORS",
    "DEEP_WATER_COLOR",
    "FALLBACK_LAND_COLOR",
    "GRID_LINE_COLOR",
    "HUD_BACKGROUND_COLOR",
    "HUD_TEXT_COLOR",
    "INLAND_WATER_COLOR",
    "RIVER_COLOR",
    "SHALLOW_WATER_COLOR",
    "WATER_COLOR",
    "get_tile_fill_color",
]
