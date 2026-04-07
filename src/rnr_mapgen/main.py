"""Command-line entry point for the RiftandReign scalar-field groundwork."""

from rnr_mapgen.board import create_empty_map
from rnr_mapgen.fields import generate_scalar_fields, summarize_scalar_fields
from rnr_mapgen.types import GeneratorConfig


def main() -> int:
    """Build a deterministic board, apply scalar fields, and print a summary."""
    config = GeneratorConfig(width=4, height=3, seed=0)
    map_data = create_empty_map(config)
    generate_scalar_fields(map_data)
    print(summarize_scalar_fields(map_data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
