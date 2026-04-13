import pytest

from rnr_mapgen.biomes import classify_biomes
from rnr_mapgen.board import create_empty_map
from rnr_mapgen.cli import parse_args
from rnr_mapgen.fields import generate_scalar_fields
from rnr_mapgen.hydrology import generate_hydrology
from rnr_mapgen.starts import score_start_suitability, summarize_starts
from rnr_mapgen.terrain import classify_terrain
from rnr_mapgen.types import GeneratorConfig


def _build_full_map(config: GeneratorConfig):
    map_data = create_empty_map(config)
    generate_scalar_fields(map_data)
    classify_terrain(map_data)
    generate_hydrology(map_data)
    classify_biomes(map_data)
    score_start_suitability(map_data)
    return map_data


def test_parse_args_reads_width_height_and_seed() -> None:
    config = parse_args(["--width", "24", "--height", "16", "--seed", "5"])

    assert config.width == 24
    assert config.height == 16
    assert config.seed == 5


def test_invalid_dimensions_are_rejected_cleanly() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--width", "0", "--height", "16", "--seed", "1"])


def test_default_cli_config_is_stable() -> None:
    config = parse_args([])

    assert config.width == 24
    assert config.height == 16
    assert config.seed == 0
    assert config.preview_width == 24
    assert config.preview_height == 12


def test_explicit_config_produces_deterministic_results() -> None:
    config = parse_args(["--width", "24", "--height", "16", "--seed", "7"])

    first = _build_full_map(config)
    second = _build_full_map(config)

    assert first == second


def test_larger_map_config_preserves_pipeline_without_crashing() -> None:
    config = parse_args(["--width", "32", "--height", "20", "--seed", "11"])

    map_data = _build_full_map(config)

    assert map_data.width == 32
    assert map_data.height == 20
    assert map_data.tile_count == 640


def test_preview_output_is_non_empty_and_deterministic_for_large_map() -> None:
    config = parse_args(
        [
            "--width",
            "32",
            "--height",
            "20",
            "--seed",
            "11",
            "--preview-width",
            "18",
            "--preview-height",
            "8",
        ]
    )

    first = summarize_starts(_build_full_map(config))
    second = summarize_starts(_build_full_map(config))

    assert first
    assert first == second
    assert "ASCII preview policy: top-left crop up to 18x8." in first


def test_full_pipeline_preserves_config_through_larger_map() -> None:
    config = parse_args(
        ["--width", "28", "--height", "18", "--seed", "9", "--sea-level", "0.41"]
    )

    map_data = _build_full_map(config)

    assert map_data.config == config
    assert map_data.seed == 9
