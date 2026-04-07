# Step 0002 - Board Foundation

## Step Name

Deterministic finite board foundation.

## Purpose

Add the first real board/data layer for the map generator by creating a finite non-wrapping playable field of pointy-top axial hexes, populating placeholder tile records for every coordinate, exposing a clean creation API, and adding a concise debug-oriented CLI summary.

## Files Changed Or Created

- `README.md`
- `CHANGELOG.md`
- `docs/data_model.md`
- `docs/repo_index.md`
- `docs/changes/0002_board_foundation.md`
- `src/rnr_mapgen/board.py`
- `src/rnr_mapgen/main.py`
- `src/rnr_mapgen/types.py`
- `tests/test_board.py`

## Important Decisions Made

- The playable field is defined as a finite row-major rectangular axial board with `q` in `0..width-1` and `r` in `0..height-1`.
- Board construction is deterministic and seed-aware at the metadata level even though seed-driven terrain behavior is not implemented yet.
- `create_empty_map(config)` is the primary API for constructing the current board state.
- The CLI remains intentionally small and prints a compact summary rather than attempting visualization.
- Out-of-bounds neighbors are handled by board membership checks instead of coordinate wrapping.

## Assumptions Made

- A simple rectangular axial board is the most practical and auditable substrate for the next terrain-generation steps.
- Placeholder defaults on each `TileData` record are sufficient until the terrain pipeline begins to populate real values.
- Dimension validation belongs in `GeneratorConfig` so invalid boards fail early and clearly.

## Work Intentionally Deferred

- scalar field generation
- land or water shaping
- elevation modeling
- rivers and lakes logic
- climate modeling
- biome classification
- start-region validation logic
- any rendering or external visualization framework
- any gameplay systems outside map construction
