# Step 0005 - First-Pass Hydrology

## Step Name

Deterministic first-pass hydrology groundwork.

## Purpose

Add the first simple hydrology layer on top of the existing scalar fields and land or water classification by computing downhill outflow targets, simple flow accumulation, sparse river marking, and a river-aware ASCII preview in the CLI.

## Files Changed Or Created

- `README.md`
- `CHANGELOG.md`
- `docs/acceptance_tests.md`
- `docs/data_model.md`
- `docs/dev_workflow.md`
- `docs/generator_pipeline.md`
- `docs/map_spec.md`
- `docs/repo_index.md`
- `docs/changes/0005_first_pass_hydrology.md`
- `src/rnr_mapgen/hydrology.py`
- `src/rnr_mapgen/main.py`
- `src/rnr_mapgen/types.py`
- `tests/test_hydrology.py`

## Important Decisions Made

- Hydrology uses deterministic steepest-descent routing from land tiles based on lower neighboring elevation.
- Flow accumulation is computed in descending elevation order so upstream contribution is stable and easy to inspect.
- River marking remains sparse by using a named accumulation threshold and only marking land tiles, including strong local sink termini.
- The CLI preview now uses `~` for river tiles on land while retaining `#` for land and `.` for water.
- Windows workflow docs now explicitly use `.\.venv\Scripts\Activate.ps1` for PowerShell activation.

## Assumptions Made

- A simple steepest-descent plus accumulation model is sufficient groundwork before any more advanced hydrology work.
- First-pass rivers should prefer readability and deterministic behavior over realism at this stage.
- Land tiles with no lower neighbor can terminate locally for now without simulating full basin or lake behavior.

## Work Intentionally Deferred

- biome assignment
- start-region validation logic
- erosion simulation
- basin filling
- lake simulation
- refined river edge representation
- rendering, GUI, or external visualization frameworks
- any gameplay systems outside map generation
