from rnr_mapgen.board import create_empty_map
from rnr_mapgen.fields import generate_scalar_fields
from rnr_mapgen.types import GeneratorConfig


def test_scalar_fields_are_repeatable_for_same_seed() -> None:
    config = GeneratorConfig(width=5, height=4, seed=123)

    first = generate_scalar_fields(create_empty_map(config))
    second = generate_scalar_fields(create_empty_map(config))

    assert first == second


def test_different_seeds_change_scalar_values() -> None:
    first = generate_scalar_fields(
        create_empty_map(GeneratorConfig(width=5, height=4, seed=1))
    )
    second = generate_scalar_fields(
        create_empty_map(GeneratorConfig(width=5, height=4, seed=2))
    )

    first_values = [
        (tile.elevation, tile.moisture, tile.temperature)
        for tile in first.tiles.values()
    ]
    second_values = [
        (tile.elevation, tile.moisture, tile.temperature)
        for tile in second.tiles.values()
    ]

    assert first_values != second_values


def test_scalar_values_stay_in_unit_interval() -> None:
    map_data = generate_scalar_fields(
        create_empty_map(GeneratorConfig(width=6, height=5, seed=77))
    )

    for tile in map_data.tiles.values():
        assert 0.0 <= tile.elevation <= 1.0
        assert 0.0 <= tile.moisture <= 1.0
        assert 0.0 <= tile.temperature <= 1.0


def test_every_tile_receives_scalar_values() -> None:
    map_data = generate_scalar_fields(
        create_empty_map(GeneratorConfig(width=4, height=3, seed=8))
    )

    assert all(
        tile.elevation != 0.0 or tile.moisture != 0.0 or tile.temperature != 0.0
        for tile in map_data.tiles.values()
    )


def test_metadata_is_preserved_after_field_generation() -> None:
    config = GeneratorConfig(width=7, height=2, seed=91)

    map_data = generate_scalar_fields(create_empty_map(config))

    assert map_data.width == 7
    assert map_data.height == 2
    assert map_data.seed == 91
    assert map_data.config == config
