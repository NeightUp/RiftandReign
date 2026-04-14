from rnr_mapgen.board import create_empty_map
from rnr_mapgen.fields import generate_scalar_fields
from rnr_mapgen.hydrology import generate_hydrology, render_ascii_preview
from rnr_mapgen.terrain import classify_terrain
from rnr_mapgen.types import GeneratorConfig


def _build_map(config: GeneratorConfig):
    map_data = create_empty_map(config)
    generate_scalar_fields(map_data)
    classify_terrain(map_data)
    generate_hydrology(map_data)
    return map_data


def test_hydrology_is_repeatable_for_same_seed() -> None:
    config = GeneratorConfig(width=12, height=8, seed=0)

    first = _build_map(config)
    second = _build_map(config)

    assert first == second


def test_hydrology_preserves_metadata_and_scalar_values() -> None:
    config = GeneratorConfig(width=12, height=8, seed=3)
    map_data = create_empty_map(config)
    generate_scalar_fields(map_data)
    classify_terrain(map_data)
    before_scalars = {
        coord: (tile.elevation, tile.moisture, tile.temperature)
        for coord, tile in map_data.tiles.items()
    }

    generate_hydrology(map_data)

    after_scalars = {
        coord: (tile.elevation, tile.moisture, tile.temperature)
        for coord, tile in map_data.tiles.items()
    }

    assert map_data.width == 12
    assert map_data.height == 8
    assert map_data.seed == 3
    assert map_data.config == config
    assert before_scalars == after_scalars


def test_rivers_only_appear_on_land_tiles() -> None:
    map_data = _build_map(GeneratorConfig(width=12, height=8, seed=0))

    assert all(not tile.is_water for tile in map_data.tiles.values() if tile.has_river)


def test_downhill_routing_never_points_uphill() -> None:
    map_data = _build_map(GeneratorConfig(width=12, height=8, seed=0))

    for tile in map_data.tiles.values():
        if tile.river_flow_to is None:
            continue

        target = map_data.tiles[tile.river_flow_to]
        if target.is_water:
            continue
        assert target.elevation < tile.elevation


def test_large_default_style_map_has_meaningful_river_presence() -> None:
    map_data = _build_map(GeneratorConfig(width=50, height=30, seed=0))

    river_tiles = sum(1 for tile in map_data.tiles.values() if tile.has_river)

    assert river_tiles >= 12


def test_visible_river_tiles_are_a_selected_subset_of_drainage_paths() -> None:
    map_data = _build_map(GeneratorConfig(width=32, height=20, seed=0))

    visible_river_tiles = sum(1 for tile in map_data.tiles.values() if tile.has_river)
    routed_land_tiles = sum(
        1
        for tile in map_data.tiles.values()
        if not tile.is_water and tile.river_flow_to is not None
    )

    assert visible_river_tiles < routed_land_tiles


def test_large_map_river_network_is_present_but_not_absurdly_saturated() -> None:
    map_data = _build_map(GeneratorConfig(width=50, height=30, seed=7))

    land_tiles = sum(1 for tile in map_data.tiles.values() if not tile.is_water)
    visible_river_tiles = sum(1 for tile in map_data.tiles.values() if tile.has_river)
    river_ratio = visible_river_tiles / land_tiles

    assert 0.01 <= river_ratio <= 0.18


def test_visible_river_channels_do_not_bifurcate_inland() -> None:
    map_data = _build_map(GeneratorConfig(width=50, height=30, seed=0))

    for tile in map_data.tiles.values():
        if not tile.has_river:
            continue
        if tile.river_flow_to is None:
            continue

        target = map_data.tiles[tile.river_flow_to]
        if target.is_water:
            continue

        assert target.has_river


def test_visible_rivers_terminate_coherently() -> None:
    map_data = _build_map(GeneratorConfig(width=24, height=16, seed=0))

    for tile in map_data.tiles.values():
        if not tile.has_river:
            continue

        if tile.river_flow_to is None:
            continue

        target = map_data.tiles[tile.river_flow_to]
        assert target.is_water or target.has_river or target.flow_accumulation >= tile.flow_accumulation


def test_ascii_preview_with_rivers_has_stable_shape() -> None:
    map_data = _build_map(GeneratorConfig(width=4, height=3, seed=0))

    preview = render_ascii_preview(map_data)
    lines = preview.splitlines()

    assert preview
    assert len(lines) == 3
    assert len(lines[0]) == 4
    assert len(lines[1].lstrip()) == 4
    assert len(lines[2]) == 4
