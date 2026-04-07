"""Command-line entry point for the RiftandReign hydrology groundwork."""

from rnr_mapgen.board import create_empty_map
from rnr_mapgen.fields import generate_scalar_fields
from rnr_mapgen.hydrology import generate_hydrology, summarize_hydrology
from rnr_mapgen.terrain import classify_terrain
from rnr_mapgen.types import GeneratorConfig


def main() -> int:
    """Build a deterministic board, add hydrology groundwork, and print a summary."""
    config = GeneratorConfig(width=12, height=8, seed=0)
    map_data = create_empty_map(config)
    generate_scalar_fields(map_data)
    classify_terrain(map_data)
    generate_hydrology(map_data)
    print(summarize_hydrology(map_data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
