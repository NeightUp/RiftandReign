"""Command-line entry point for the RiftandReign application shell."""

from __future__ import annotations

import sys

from rnr_mapgen.application.cli import parse_args
from rnr_mapgen.generation.pipeline import generate_world
from rnr_mapgen.rendering.viewer import run_viewer
from rnr_mapgen.starts import summarize_starts
from rnr_mapgen.types import GeneratorConfig, MapData


def generate_map(config: GeneratorConfig) -> MapData:
    """Compatibility wrapper around the current world-generation pipeline."""
    return generate_world(config)


def main(argv: list[str] | None = None) -> int:
    """Build a deterministic board and either print or render a debug view."""
    options = parse_args(argv)
    map_data = generate_map(options.config)

    if not options.viewer.enabled:
        print(summarize_starts(map_data))
        return 0

    try:
        return run_viewer(map_data)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
