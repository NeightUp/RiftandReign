from rnr_mapgen.biomes import classify_biomes
from rnr_mapgen.board import create_empty_map
from rnr_mapgen.fields import generate_scalar_fields
from rnr_mapgen.hydrology import generate_hydrology
from rnr_mapgen.starts import get_top_start_candidates, score_start_suitability
from rnr_mapgen.terrain import classify_terrain
from rnr_mapgen.types import GeneratorConfig


def _build_map(config: GeneratorConfig):
    map_data = create_empty_map(config)
    generate_scalar_fields(map_data)
    classify_terrain(map_data)
    generate_hydrology(map_data)
    classify_biomes(map_data)
    score_start_suitability(map_data)
    return map_data


def test_start_scoring_is_repeatable_for_same_seed() -> None:
    config = GeneratorConfig(width=12, height=8, seed=0)

    first = _build_map(config)
    second = _build_map(config)

    assert first == second


def test_water_tiles_are_never_start_candidates() -> None:
    map_data = _build_map(GeneratorConfig(width=12, height=8, seed=0))

    assert all(not tile.is_start_candidate for tile in map_data.tiles.values() if tile.is_water)


def test_mountain_tiles_are_never_start_candidates() -> None:
    map_data = _build_map(GeneratorConfig(width=12, height=8, seed=0))

    assert all(
        not tile.is_start_candidate
        for tile in map_data.tiles.values()
        if tile.biome == "mountains"
    )


def test_default_config_has_some_start_candidates() -> None:
    map_data = _build_map(GeneratorConfig(width=12, height=8, seed=0))

    assert any(tile.is_start_candidate for tile in map_data.tiles.values())


def test_candidate_sorting_is_deterministic() -> None:
    map_data = _build_map(GeneratorConfig(width=12, height=8, seed=0))

    first = [(tile.coord.q, tile.coord.r, tile.start_suitability) for tile in get_top_start_candidates(map_data)]
    second = [(tile.coord.q, tile.coord.r, tile.start_suitability) for tile in get_top_start_candidates(map_data)]

    assert first == second


def test_start_scoring_preserves_previous_layers() -> None:
    config = GeneratorConfig(width=12, height=8, seed=5)
    map_data = create_empty_map(config)
    generate_scalar_fields(map_data)
    classify_terrain(map_data)
    generate_hydrology(map_data)
    classify_biomes(map_data)
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
            tile.biome,
        )
        for coord, tile in map_data.tiles.items()
    }

    score_start_suitability(map_data)

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
            tile.biome,
        )
        for coord, tile in map_data.tiles.items()
    }

    assert before_state == after_state


def test_top_candidates_are_stable_and_non_empty() -> None:
    map_data = _build_map(GeneratorConfig(width=12, height=8, seed=0))

    top = get_top_start_candidates(map_data)

    assert top
    assert top == sorted(
        top,
        key=lambda tile: (
            -(tile.start_suitability or float("-inf")),
            tile.display_row,
            tile.display_col,
            tile.coord.q,
        ),
    )
