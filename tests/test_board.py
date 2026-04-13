from rnr_mapgen.board import axial_to_display, create_empty_map, display_to_axial, iter_board_coords
from rnr_mapgen.hex import HexCoord
from rnr_mapgen.types import GeneratorConfig


def test_expected_tile_count_for_dimensions() -> None:
    config = GeneratorConfig(width=4, height=3, seed=7)

    map_data = create_empty_map(config)

    assert map_data.tile_count == 12


def test_full_rectangular_board_area_is_present() -> None:
    config = GeneratorConfig(width=3, height=3, seed=99)

    map_data = create_empty_map(config)

    expected = {
        HexCoord(q=0, r=0),
        HexCoord(q=1, r=0),
        HexCoord(q=2, r=0),
        HexCoord(q=0, r=1),
        HexCoord(q=1, r=1),
        HexCoord(q=2, r=1),
        HexCoord(q=-1, r=2),
        HexCoord(q=0, r=2),
        HexCoord(q=1, r=2),
    }
    assert set(map_data.tiles) == expected


def test_repeated_creation_with_same_config_matches() -> None:
    config = GeneratorConfig(width=5, height=4, seed=1234)

    first = create_empty_map(config)
    second = create_empty_map(config)

    assert first == second


def test_map_metadata_is_preserved() -> None:
    config = GeneratorConfig(width=6, height=2, seed=42)

    map_data = create_empty_map(config)

    assert map_data.width == 6
    assert map_data.height == 2
    assert map_data.seed == 42
    assert map_data.config == config


def test_center_tile_neighbors_are_compatible_with_board_membership() -> None:
    config = GeneratorConfig(width=4, height=4, seed=11)
    map_data = create_empty_map(config)
    center = HexCoord(q=1, r=1)

    in_bounds_neighbors = [
        neighbor for neighbor in center.list_neighbors() if map_data.contains(neighbor)
    ]

    assert len(in_bounds_neighbors) == 6
    assert all(map_data.tiles[neighbor].coord == neighbor for neighbor in in_bounds_neighbors)


def test_iter_board_coords_is_row_major() -> None:
    coords = iter_board_coords(width=3, height=3)

    assert coords == [
        HexCoord(q=0, r=0),
        HexCoord(q=1, r=0),
        HexCoord(q=2, r=0),
        HexCoord(q=0, r=1),
        HexCoord(q=1, r=1),
        HexCoord(q=2, r=1),
        HexCoord(q=-1, r=2),
        HexCoord(q=0, r=2),
        HexCoord(q=1, r=2),
    ]


def test_display_and_axial_layout_helpers_round_trip() -> None:
    coord = display_to_axial(display_col=4, display_row=6)

    assert axial_to_display(coord) == (4, 6)
