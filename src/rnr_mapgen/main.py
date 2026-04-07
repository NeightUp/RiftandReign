"""Command-line entry point for the RiftandReign terrain first pass."""

from rnr_mapgen.board import create_empty_map
from rnr_mapgen.fields import generate_scalar_fields
from rnr_mapgen.terrain import classify_terrain, summarize_terrain
from rnr_mapgen.types import GeneratorConfig


def main() -> int:
    """Build a deterministic board, classify first-pass terrain, and print a summary."""
    config = GeneratorConfig(width=12, height=8, seed=0)
    map_data = create_empty_map(config)
    generate_scalar_fields(map_data)
    classify_terrain(map_data)
    print(summarize_terrain(map_data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
