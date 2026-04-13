"""Board construction utilities for the deterministic map foundation."""

from __future__ import annotations

from rnr_mapgen.hex import HexCoord
from rnr_mapgen.types import GeneratorConfig, MapData, TileData


def iter_board_coords(width: int, height: int) -> list[HexCoord]:
    """Return row-major axial coordinates for the rectangular display field."""
    return [
        display_to_axial(display_col=display_col, display_row=display_row)
        for display_row in range(height)
        for display_col in range(width)
    ]


def iter_display_positions(width: int, height: int) -> list[tuple[int, int, HexCoord]]:
    """Return row-major display positions paired with their axial coordinates."""
    return [
        (
            display_col,
            display_row,
            display_to_axial(display_col=display_col, display_row=display_row),
        )
        for display_row in range(height)
        for display_col in range(width)
    ]


def display_to_axial(display_col: int, display_row: int) -> HexCoord:
    """Convert an odd-row offset display position into axial storage coordinates."""
    q = display_col - ((display_row - (display_row & 1)) // 2)
    return HexCoord(q=q, r=display_row)


def axial_to_display(coord: HexCoord) -> tuple[int, int]:
    """Convert an axial storage coordinate into an odd-row display position."""
    display_col = coord.q + ((coord.r - (coord.r & 1)) // 2)
    return display_col, coord.r


def create_empty_map(config: GeneratorConfig) -> MapData:
    """Build a deterministic empty map with placeholder tile data."""
    tiles = {
        coord: TileData(
            coord=coord,
            display_col=display_col,
            display_row=display_row,
        )
        for display_col, display_row, coord in iter_display_positions(
            width=config.width,
            height=config.height,
        )
    }
    return MapData(
        width=config.width,
        height=config.height,
        seed=config.seed,
        config=config,
        tiles=tiles,
    )
