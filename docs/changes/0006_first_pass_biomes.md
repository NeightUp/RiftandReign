# Step 0006 - First-Pass Biomes

## Step Name

Deterministic first-pass biome classification.

## Purpose

Add a readable world-layer classification on top of the existing scalar fields, land and water classification, and first-pass hydrology by assigning a compact set of land biome labels and exposing them clearly in the CLI summary and ASCII preview.

## Files Changed Or Created

- `README.md`
- `CHANGELOG.md`
- `docs/acceptance_tests.md`
- `docs/data_model.md`
- `docs/generator_pipeline.md`
- `docs/map_spec.md`
- `docs/repo_index.md`
- `docs/changes/0006_first_pass_biomes.md`
- `src/rnr_mapgen/biomes.py`
- `src/rnr_mapgen/main.py`
- `tests/test_biomes.py`

## Important Decisions Made

- The first-pass biome set stays compact: plains, forest, desert, tundra, hills, and mountains.
- Biomes are assigned only to land tiles; water remains visually and structurally separate.
- Elevation drives mountains and hills first, then temperature, moisture, and a light river bonus shape lower-elevation land biomes.
- The CLI preview keeps `.` for water and `~` for river tiles, with simple lowercase biome markers for the remaining land tiles.

## Assumptions Made

- A small, explicit biome set is more useful than a broader taxonomy at this stage.
- River presence can gently support greener land without becoming a full climate or fertility model.
- Plains should remain the broad fallback biome when land does not strongly qualify for another type.

## Work Intentionally Deferred

- start-region validation logic
- full climate simulation
- erosion
- biome refinement beyond the first-pass set
- rendering, GUI, or external visualization frameworks
- any gameplay systems outside map generation
