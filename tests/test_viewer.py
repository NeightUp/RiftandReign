from rnr_mapgen.board import create_empty_map
from rnr_mapgen.hex import HexCoord
from rnr_mapgen.types import GeneratorConfig
from rnr_mapgen.viewer import (
    DEFAULT_HEX_RADIUS,
    ViewState,
    axial_round,
    hex_to_world,
    map_pixel_bounds,
    screen_to_hex_coord,
    world_to_hex,
    world_to_screen,
)


def test_hex_world_conversion_round_trips_to_same_coord() -> None:
    coord = HexCoord(q=4, r=3)
    world_x, world_y = hex_to_world(coord, DEFAULT_HEX_RADIUS)

    assert world_to_hex(world_x, world_y, DEFAULT_HEX_RADIUS) == coord


def test_axial_round_snaps_fractional_point_to_nearest_hex() -> None:
    assert axial_round(2.49, 1.51) == HexCoord(q=2, r=2)


def test_screen_to_hex_coord_uses_view_transform_consistently() -> None:
    map_data = create_empty_map(GeneratorConfig(width=6, height=4, seed=0))
    coord = HexCoord(q=3, r=2)
    view_state = ViewState(offset_x=120.0, offset_y=80.0, zoom=1.25)
    screen_x, screen_y = world_to_screen(hex_to_world(coord, DEFAULT_HEX_RADIUS), view_state)

    found = screen_to_hex_coord(
        map_data=map_data,
        screen_pos=(int(round(screen_x)), int(round(screen_y))),
        view_state=view_state,
    )

    assert found == coord


def test_map_pixel_bounds_expand_with_board_size() -> None:
    small_map = create_empty_map(GeneratorConfig(width=2, height=2, seed=0))
    large_map = create_empty_map(GeneratorConfig(width=6, height=4, seed=0))

    small_bounds = map_pixel_bounds(small_map, DEFAULT_HEX_RADIUS)
    large_bounds = map_pixel_bounds(large_map, DEFAULT_HEX_RADIUS)

    assert (large_bounds[2] - large_bounds[0]) > (small_bounds[2] - small_bounds[0])
    assert (large_bounds[3] - large_bounds[1]) > (small_bounds[3] - small_bounds[1])
