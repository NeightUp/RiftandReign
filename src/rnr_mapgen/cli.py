"""CLI helpers for configuring the RiftandReign map generator."""

from __future__ import annotations

import argparse

from rnr_mapgen.types import GeneratorConfig


DEFAULT_WIDTH = 24
DEFAULT_HEIGHT = 16
DEFAULT_SEED = 0
DEFAULT_PREVIEW_WIDTH = 24
DEFAULT_PREVIEW_HEIGHT = 12


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for the map generator."""
    parser = argparse.ArgumentParser(
        prog="rnr-mapgen",
        description="Generate a deterministic debug-oriented RiftandReign map summary.",
    )
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH, help="Map width in axial columns.")
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT, help="Map height in axial rows.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Deterministic map seed.")
    parser.add_argument(
        "--sea-level",
        dest="sea_level_threshold",
        type=float,
        default=GeneratorConfig.__dataclass_fields__["sea_level_threshold"].default,
        help="Land or water threshold applied during first-pass terrain classification.",
    )
    parser.add_argument(
        "--river-source-threshold",
        dest="river_source_threshold",
        type=float,
        default=GeneratorConfig.__dataclass_fields__["river_source_threshold"].default,
        help="Minimum flow accumulation needed to mark a first-pass river tile.",
    )
    parser.add_argument(
        "--preview-width",
        type=int,
        default=DEFAULT_PREVIEW_WIDTH,
        help="Maximum ASCII preview width before deterministic clipping.",
    )
    parser.add_argument(
        "--preview-height",
        type=int,
        default=DEFAULT_PREVIEW_HEIGHT,
        help="Maximum ASCII preview height before deterministic clipping.",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> GeneratorConfig:
    """Parse CLI arguments into a validated generator configuration."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return GeneratorConfig(
            width=args.width,
            height=args.height,
            seed=args.seed,
            sea_level_threshold=args.sea_level_threshold,
            river_source_threshold=args.river_source_threshold,
            preview_width=args.preview_width,
            preview_height=args.preview_height,
        )
    except ValueError as exc:
        parser.error(str(exc))
