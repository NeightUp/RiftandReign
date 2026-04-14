"""Board construction and layout helpers."""

from __future__ import annotations

from rnr_mapgen.domain.hex import HexCoord
from rnr_mapgen.domain.models import GeneratorConfig, MapData, TileData


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
    """Build an empty map populated with per-tile domain objects."""
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


def wrap_display_col(width: int, display_col: int) -> int:
    """Wrap a display column into the map width."""
    return display_col % width


def wrap_axial_horizontal(map_data: MapData, coord: HexCoord) -> HexCoord | None:
    """Wrap one axial coordinate horizontally if its row is valid."""
    display_col, display_row = axial_to_display(coord)
    if display_row < 0 or display_row >= map_data.height:
        return None
    return display_to_axial(wrap_display_col(map_data.width, display_col), display_row)


def iter_neighbor_coords(map_data: MapData, coord: HexCoord) -> list[HexCoord]:
    """Return neighboring coordinates using cylindrical east/west wrapping."""
    neighbors: list[HexCoord] = []
    seen: set[HexCoord] = set()

    for neighbor in coord.list_neighbors():
        if neighbor in map_data.tiles:
            if neighbor not in seen:
                neighbors.append(neighbor)
                seen.add(neighbor)
            continue

        wrapped_neighbor = wrap_axial_horizontal(map_data, neighbor)
        if wrapped_neighbor is None or wrapped_neighbor not in map_data.tiles:
            continue
        if wrapped_neighbor in seen:
            continue
        neighbors.append(wrapped_neighbor)
        seen.add(wrapped_neighbor)

    return neighbors
