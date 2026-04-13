"""Command-line entry point for the RiftandReign configurable map generator."""

from __future__ import annotations

import sys

from rnr_mapgen.biomes import classify_biomes
from rnr_mapgen.board import create_empty_map
from rnr_mapgen.cli import parse_args
from rnr_mapgen.fields import generate_scalar_fields
from rnr_mapgen.hydrology import generate_hydrology
from rnr_mapgen.starts import score_start_suitability, summarize_starts
from rnr_mapgen.terrain import classify_terrain
from rnr_mapgen.types import GeneratorConfig, MapData


def generate_map(config: GeneratorConfig) -> MapData:
    """Run the deterministic generation pipeline and return the completed map."""
    map_data = create_empty_map(config)
    generate_scalar_fields(map_data)
    classify_terrain(map_data)
    generate_hydrology(map_data)
    classify_biomes(map_data)
    score_start_suitability(map_data)
    return map_data


def main(argv: list[str] | None = None) -> int:
    """Build a deterministic board and either print or render a debug view."""
    options = parse_args(argv)
    map_data = generate_map(options.config)

    if not options.viewer.enabled:
        print(summarize_starts(map_data))
        return 0

    from rnr_mapgen.viewer import run_viewer

    try:
        return run_viewer(map_data)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
