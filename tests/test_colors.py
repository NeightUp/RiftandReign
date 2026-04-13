from rnr_mapgen.colors import BIOME_COLORS, WATER_COLOR, get_tile_fill_color
from rnr_mapgen.hex import HexCoord
from rnr_mapgen.types import TileData


def test_water_tiles_use_water_debug_color() -> None:
    tile = TileData(coord=HexCoord(0, 0), is_water=True)

    assert get_tile_fill_color(tile) == WATER_COLOR


def test_land_biomes_map_to_named_debug_colors() -> None:
    tile = TileData(coord=HexCoord(2, 1), biome="forest")

    assert get_tile_fill_color(tile) == BIOME_COLORS["forest"]
