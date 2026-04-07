# Step 0004 - Land And Water Classification

## Step Name

Deterministic first-pass land and water classification.

## Purpose

Turn the scalar-field groundwork into the first map-like terrain output by classifying every tile as land or water, exposing a compact ASCII terrain preview in the CLI, and updating the project documentation to reflect the new terrain layer and the actual Windows development workflow.

## Files Changed Or Created

- `README.md`
- `CHANGELOG.md`
- `docs/acceptance_tests.md`
- `docs/data_model.md`
- `docs/generator_pipeline.md`
- `docs/map_spec.md`
- `docs/repo_index.md`
- `docs/changes/0004_land_water_classification.md`
- `src/rnr_mapgen/fields.py`
- `src/rnr_mapgen/main.py`
- `src/rnr_mapgen/terrain.py`
- `tests/test_terrain.py`

## Important Decisions Made

- Land and water classification is driven primarily by elevation with explicit edge-water bias and small support from existing moisture and temperature fields.
- A light cleanup pass removes isolated one-tile land noise and allows strongly supported water tiles to join larger land masses.
- The CLI now shows land and water counts, land percentage, scalar ranges, and an ASCII preview using `#` for land and `.` for water.
- The default CLI board size was increased to make the first-pass terrain preview more informative.

## Assumptions Made

- A simple, deterministic, tunable classifier is more valuable at this stage than a more complex terrain system.
- A modest edge-water bias helps produce more useful early coastlines for future 4X-oriented map work.
- The existing scalar fields should remain intact and reusable by later hydrology and biome systems.

## Work Intentionally Deferred

- rivers
- hydrology
- flow accumulation
- lakes as a water-system simulation
- biome assignment
- start-region validation logic
- rendering, GUI, or external visualization frameworks
- any gameplay systems outside map generation
