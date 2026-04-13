from collections import deque

from rnr_mapgen.board import create_empty_map
from rnr_mapgen.fields import generate_scalar_fields
from rnr_mapgen.terrain import classify_terrain, render_ascii_terrain
from rnr_mapgen.types import GeneratorConfig


def test_terrain_classification_is_repeatable_for_same_seed() -> None:
    config = GeneratorConfig(width=12, height=8, seed=0)

    first = classify_terrain(generate_scalar_fields(create_empty_map(config)))
    second = classify_terrain(generate_scalar_fields(create_empty_map(config)))

    assert first == second


def test_terrain_classification_populates_is_water_for_every_tile() -> None:
    map_data = classify_terrain(
        generate_scalar_fields(create_empty_map(GeneratorConfig(width=8, height=6, seed=3)))
    )

    assert all(isinstance(tile.is_water, bool) for tile in map_data.tiles.values())


def test_default_like_config_contains_land_and_water() -> None:
    map_data = classify_terrain(
        generate_scalar_fields(create_empty_map(GeneratorConfig(width=12, height=8, seed=0)))
    )

    land_tiles = sum(1 for tile in map_data.tiles.values() if not tile.is_water)
    water_tiles = sum(1 for tile in map_data.tiles.values() if tile.is_water)

    assert land_tiles > 0
    assert water_tiles > 0


def test_different_seeds_change_terrain_layout() -> None:
    first = classify_terrain(
        generate_scalar_fields(create_empty_map(GeneratorConfig(width=12, height=8, seed=1)))
    )
    second = classify_terrain(
        generate_scalar_fields(create_empty_map(GeneratorConfig(width=12, height=8, seed=2)))
    )

    first_layout = [tile.is_water for tile in first.tiles.values()]
    second_layout = [tile.is_water for tile in second.tiles.values()]

    assert first_layout != second_layout


def test_terrain_classification_preserves_metadata_and_scalars() -> None:
    config = GeneratorConfig(width=10, height=7, seed=9)
    map_data = generate_scalar_fields(create_empty_map(config))
    before_scalars = {
        coord: (tile.elevation, tile.moisture, tile.temperature)
        for coord, tile in map_data.tiles.items()
    }

    classify_terrain(map_data)

    after_scalars = {
        coord: (tile.elevation, tile.moisture, tile.temperature)
        for coord, tile in map_data.tiles.items()
    }

    assert map_data.width == 10
    assert map_data.height == 7
    assert map_data.seed == 9
    assert map_data.config == config
    assert before_scalars == after_scalars


def test_ascii_preview_has_consistent_shape() -> None:
    map_data = classify_terrain(
        generate_scalar_fields(create_empty_map(GeneratorConfig(width=4, height=3, seed=0)))
    )

    preview = render_ascii_terrain(map_data)
    lines = preview.splitlines()

    assert preview
    assert len(lines) == 3
    assert len(lines[0]) == 4
    assert len(lines[1].lstrip()) == 4
    assert len(lines[2]) == 4


def test_default_large_map_land_ratio_stays_in_practical_range() -> None:
    map_data = classify_terrain(
        generate_scalar_fields(create_empty_map(GeneratorConfig(width=24, height=16, seed=0)))
    )

    land_ratio = sum(1 for tile in map_data.tiles.values() if not tile.is_water) / map_data.tile_count

    assert 0.28 <= land_ratio <= 0.68


def test_many_large_map_seeds_support_multiple_major_land_regions() -> None:
    seeds_with_multiple_regions = 0

    for seed in range(8):
        map_data = classify_terrain(
            generate_scalar_fields(create_empty_map(GeneratorConfig(width=32, height=20, seed=seed)))
        )
        major_regions = [
            region for region in _collect_land_regions(map_data)
            if len(region) >= 20
        ]
        if len(major_regions) >= 2:
            seeds_with_multiple_regions += 1

    assert seeds_with_multiple_regions >= 4


def _collect_land_regions(map_data) -> list[set]:
    regions: list[set] = []
    visited = set()

    for coord, tile in map_data.tiles.items():
        if tile.is_water or coord in visited:
            continue

        region = set()
        frontier = deque([coord])
        visited.add(coord)

        while frontier:
            current = frontier.popleft()
            region.add(current)
            for neighbor in current.list_neighbors():
                if neighbor not in map_data.tiles:
                    continue
                if neighbor in visited or map_data.tiles[neighbor].is_water:
                    continue
                visited.add(neighbor)
                frontier.append(neighbor)

        regions.append(region)

    return regions
