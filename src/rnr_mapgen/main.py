"""Command-line entry point for the RiftandReign board foundation."""

from rnr_mapgen.board import create_empty_map, format_map_summary
from rnr_mapgen.types import GeneratorConfig


def main() -> int:
    """Build and display a deterministic empty board summary."""
    config = GeneratorConfig(width=4, height=3, seed=0)
    map_data = create_empty_map(config)
    print(format_map_summary(map_data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
