"""High-level deterministic world-generation pipeline."""

from __future__ import annotations

from rnr_mapgen.biomes import classify_biomes
from rnr_mapgen.generation.board import create_empty_map
from rnr_mapgen.hydrology import generate_hydrology
from rnr_mapgen.fields import generate_scalar_fields
from rnr_mapgen.starts import score_start_suitability
from rnr_mapgen.terrain import classify_terrain
from rnr_mapgen.domain.models import GeneratorConfig, MapData


def generate_world(config: GeneratorConfig) -> MapData:
    """Run the current end-to-end world-generation pipeline."""
    map_data = create_empty_map(config)
    generate_scalar_fields(map_data)
    classify_terrain(map_data)
    generate_hydrology(map_data)
    classify_biomes(map_data)
    score_start_suitability(map_data)
    return map_data
