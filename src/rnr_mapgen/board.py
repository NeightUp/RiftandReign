"""Board construction utilities for the deterministic map foundation."""

from __future__ import annotations

from rnr_mapgen.hex import HexCoord
from rnr_mapgen.types import GeneratorConfig, MapData, TileData


def iter_board_coords(width: int, height: int) -> list[HexCoord]:
    """Return row-major axial coordinates for the finite playable field."""
    return [HexCoord(q=q, r=r) for r in range(height) for q in range(width)]


def create_empty_map(config: GeneratorConfig) -> MapData:
    """Build a deterministic empty map with placeholder tile data."""
    tiles = {
        coord: TileData(coord=coord)
        for coord in iter_board_coords(width=config.width, height=config.height)
    }
    return MapData(
        width=config.width,
        height=config.height,
        seed=config.seed,
        config=config,
        tiles=tiles,
    )
