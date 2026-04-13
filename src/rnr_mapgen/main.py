"""Command-line entry point for the RiftandReign configurable map generator."""

from rnr_mapgen.biomes import classify_biomes
from rnr_mapgen.board import create_empty_map
from rnr_mapgen.cli import parse_args
from rnr_mapgen.fields import generate_scalar_fields
from rnr_mapgen.hydrology import generate_hydrology
from rnr_mapgen.starts import score_start_suitability, summarize_starts
from rnr_mapgen.terrain import classify_terrain


def main(argv: list[str] | None = None) -> int:
    """Build a deterministic board from CLI config and print a summary."""
    config = parse_args(argv)
    map_data = create_empty_map(config)
    generate_scalar_fields(map_data)
    classify_terrain(map_data)
    generate_hydrology(map_data)
    classify_biomes(map_data)
    score_start_suitability(map_data)
    print(summarize_starts(map_data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
