"""Deterministic first-pass start suitability scoring."""

from __future__ import annotations

from rnr_mapgen.hex import HexCoord
from rnr_mapgen.types import MapData, TileData


START_RADIUS = 2
MIN_NEARBY_LAND = 7
MIN_START_SCORE = 5.0
BASE_LAND_SCORE = 2.0
NEARBY_LAND_WEIGHT = 0.60
PLAINS_WEIGHT = 1.10
FOREST_WEIGHT = 0.90
RIVER_ACCESS_WEIGHT = 1.20
BIOME_VARIETY_WEIGHT = 0.35
EDGE_PENALTY_WEIGHT = 0.90
CRAMPED_WATER_PENALTY = 0.40
CRAMPED_MOUNTAIN_PENALTY = 0.50


def score_start_suitability(map_data: MapData) -> MapData:
    """Assign deterministic first-pass start suitability scores."""
    for tile in map_data.tiles.values():
        tile.start_suitability = None
        tile.is_start_candidate = False

    for coord, tile in map_data.tiles.items():
        score = _score_tile(map_data, coord, tile)
        tile.start_suitability = score
        tile.is_start_candidate = score is not None and score >= MIN_START_SCORE

    return map_data


def get_top_start_candidates(map_data: MapData, limit: int = 5) -> list[TileData]:
    """Return the highest-scoring start candidates in deterministic order."""
    candidates = [tile for tile in map_data.tiles.values() if tile.is_start_candidate]
    candidates.sort(
        key=lambda tile: (
            -(tile.start_suitability or float("-inf")),
            tile.display_row,
            tile.display_col,
            tile.coord.q,
        )
    )
    return candidates[:limit]


def summarize_starts(map_data: MapData) -> str:
    """Return a concise CLI summary including start candidate information."""
    from rnr_mapgen.biomes import render_ascii_biomes

    elevation_values = [tile.elevation for tile in map_data.tiles.values()]
    moisture_values = [tile.moisture for tile in map_data.tiles.values()]
    temperature_values = [tile.temperature for tile in map_data.tiles.values()]
    land_tiles = sum(1 for tile in map_data.tiles.values() if not tile.is_water)
    water_tiles = map_data.tile_count - land_tiles
    river_tiles = sum(1 for tile in map_data.tiles.values() if tile.has_river)
    land_percentage = (land_tiles / map_data.tile_count) * 100.0
    max_river_strength = max(
        (tile.river_strength for tile in map_data.tiles.values()),
        default=0.0,
    )
    biome_counts: dict[str, int] = {}
    for tile in map_data.tiles.values():
        if tile.biome:
            biome_counts[tile.biome] = biome_counts.get(tile.biome, 0) + 1

    top_candidates = get_top_start_candidates(map_data)
    start_eligible_tiles = sum(1 for tile in map_data.tiles.values() if tile.is_start_candidate)

    biome_lines = [f"  {biome}: {count}" for biome, count in sorted(biome_counts.items())]
    candidate_lines = [
        (
            f"  ({tile.display_col},{tile.display_row}) "
            f"score={tile.start_suitability:.2f} biome={tile.biome}"
        )
        for tile in top_candidates
    ]

    return "\n".join(
        [
            "RiftandReign first-pass start suitability groundwork.",
            f"Dimensions: {map_data.width}x{map_data.height}",
            f"Seed: {map_data.seed}",
            f"Total tiles: {map_data.tile_count}",
            f"Land tiles: {land_tiles}",
            f"Water tiles: {water_tiles}",
            f"Land percentage: {land_percentage:.1f}%",
            f"River tiles: {river_tiles}",
            f"Max river strength: {max_river_strength:.2f}",
            f"Elevation range: {min(elevation_values):.3f}..{max(elevation_values):.3f}",
            f"Moisture range: {min(moisture_values):.3f}..{max(moisture_values):.3f}",
            f"Temperature range: {min(temperature_values):.3f}..{max(temperature_values):.3f}",
            "Biome counts:",
            *biome_lines,
            f"Start-eligible tiles: {start_eligible_tiles}",
            "Top start candidates:",
            *candidate_lines,
            (
                "ASCII preview policy: top-left crop "
                f"up to {map_data.config.preview_width}x{map_data.config.preview_height}."
            ),
            "ASCII biome preview (. water, ~ river, p plains, f forest, d desert, t tundra, h hills, m mountains):",
            render_ascii_biomes(map_data),
            "Final multi-player start placement is not implemented yet.",
        ]
    )


def _score_tile(map_data: MapData, coord: HexCoord, tile: TileData) -> float | None:
    """Return the first-pass start suitability score for one tile."""
    if tile.is_water or tile.biome == "mountains":
        return None

    nearby_tiles = [
        other
        for other in map_data.tiles.values()
        if coord.distance_to(other.coord) <= START_RADIUS
    ]
    nearby_land = [other for other in nearby_tiles if not other.is_water]
    nearby_plains = sum(1 for other in nearby_land if other.biome == "plains")
    nearby_forest = sum(1 for other in nearby_land if other.biome == "forest")
    nearby_rivers = sum(1 for other in nearby_land if other.has_river)
    nearby_water = sum(1 for other in nearby_tiles if other.is_water)
    nearby_mountains = sum(1 for other in nearby_land if other.biome == "mountains")
    nearby_biomes = {other.biome for other in nearby_land if other.biome}

    if len(nearby_land) < MIN_NEARBY_LAND:
        return 0.0

    edge_penalty = _edge_penalty(coord, map_data.width, map_data.height)
    score = (
        BASE_LAND_SCORE
        + (len(nearby_land) * NEARBY_LAND_WEIGHT)
        + (nearby_plains * PLAINS_WEIGHT)
        + (nearby_forest * FOREST_WEIGHT)
        + (min(nearby_rivers, 1) * RIVER_ACCESS_WEIGHT)
        + (len(nearby_biomes) * BIOME_VARIETY_WEIGHT)
        - (edge_penalty * EDGE_PENALTY_WEIGHT)
        - (nearby_water * CRAMPED_WATER_PENALTY)
        - (nearby_mountains * CRAMPED_MOUNTAIN_PENALTY)
    )
    return max(0.0, score)


def _edge_penalty(coord: HexCoord, width: int, height: int) -> int:
    """Return a simple edge-distance penalty for cramped map borders."""
    return min(
        coord.q,
        coord.r,
        (width - 1) - coord.q,
        (height - 1) - coord.r,
    ) == 0
