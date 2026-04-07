from rnr_mapgen.biomes import classify_biomes, render_ascii_biomes
from rnr_mapgen.board import create_empty_map
from rnr_mapgen.fields import generate_scalar_fields
from rnr_mapgen.hydrology import generate_hydrology
from rnr_mapgen.terrain import classify_terrain
from rnr_mapgen.types import GeneratorConfig


def _build_map(config: GeneratorConfig):
    map_data = create_empty_map(config)
    generate_scalar_fields(map_data)
    classify_terrain(map_data)
    generate_hydrology(map_data)
    classify_biomes(map_data)
    return map_data


def test_biomes_are_repeatable_for_same_seed() -> None:
    config = GeneratorConfig(width=12, height=8, seed=0)

    first = _build_map(config)
    second = _build_map(config)

    assert first == second


def test_every_land_tile_receives_biome() -> None:
    map_data = _build_map(GeneratorConfig(width=12, height=8, seed=0))

    assert all(tile.biome for tile in map_data.tiles.values() if not tile.is_water)


def test_water_tiles_do_not_receive_land_biome() -> None:
    map_data = _build_map(GeneratorConfig(width=12, height=8, seed=0))

    assert all(tile.biome is None for tile in map_data.tiles.values() if tile.is_water)


def test_biomes_preserve_metadata_and_previous_layers() -> None:
    config = GeneratorConfig(width=12, height=8, seed=4)
    map_data = create_empty_map(config)
    generate_scalar_fields(map_data)
    classify_terrain(map_data)
    generate_hydrology(map_data)
    before_state = {
        coord: (
            tile.elevation,
            tile.moisture,
            tile.temperature,
            tile.is_water,
            tile.river_flow_to,
            tile.flow_accumulation,
            tile.has_river,
            tile.river_strength,
        )
        for coord, tile in map_data.tiles.items()
    }

    classify_biomes(map_data)

    after_state = {
        coord: (
            tile.elevation,
            tile.moisture,
            tile.temperature,
            tile.is_water,
            tile.river_flow_to,
            tile.flow_accumulation,
            tile.has_river,
            tile.river_strength,
        )
        for coord, tile in map_data.tiles.items()
    }

    assert map_data.width == 12
    assert map_data.height == 8
    assert map_data.seed == 4
    assert map_data.config == config
    assert before_state == after_state


def test_default_config_has_multiple_land_biome_types() -> None:
    map_data = _build_map(GeneratorConfig(width=12, height=8, seed=0))

    biome_types = {tile.biome for tile in map_data.tiles.values() if tile.biome}

    assert len(biome_types) >= 3


def test_ascii_biome_preview_has_stable_shape() -> None:
    map_data = _build_map(GeneratorConfig(width=4, height=3, seed=0))

    preview = render_ascii_biomes(map_data)
    lines = preview.splitlines()

    assert preview
    assert len(lines) == 3
    assert len(lines[0]) == 4
    assert len(lines[1].lstrip()) == 4
    assert len(lines[2]) == 4
