# Step 0003 - Scalar Fields

## Step Name

Deterministic scalar-field groundwork and Windows workflow documentation.

## Purpose

Add the first real data-generation layer after board construction by assigning deterministic normalized elevation, moisture, and temperature values to every tile, while also formalizing the repository's Windows virtual-environment workflow in the documentation.

## Files Changed Or Created

- `README.md`
- `CHANGELOG.md`
- `docs/acceptance_tests.md`
- `docs/data_model.md`
- `docs/dev_workflow.md`
- `docs/generator_pipeline.md`
- `docs/repo_index.md`
- `docs/changes/0003_scalar_fields.md`
- `src/rnr_mapgen/board.py`
- `src/rnr_mapgen/fields.py`
- `src/rnr_mapgen/main.py`
- `tests/test_fields.py`

## Important Decisions Made

- Scalar fields are generated with deterministic coordinate hashing, simple board-position gradients, and one local neighbor-smoothing pass.
- Scalar outputs are normalized into the `0.0..1.0` range so later stages can use them directly as input signals.
- The CLI reports scalar ranges and sample tile values instead of attempting any rendering or map classification.
- Documentation now reflects the real Windows repository workflow based on activating `.venv` and using `python` commands.

## Assumptions Made

- The repository-local virtual environment in `.venv` is the normal development path on Windows.
- A single-pass smoothing step is enough for this foundation layer and keeps the implementation easy to audit and tune later.
- Temperature, moisture, and elevation are still generic scalar signals at this stage rather than finalized gameplay-facing terrain concepts.

## Work Intentionally Deferred

- land or water classification
- coastlines
- rivers and lakes logic
- hydrology
- climate zones
- biome assignment
- start-region validation logic
- rendering, GUI, or external visualization frameworks
- any gameplay systems outside map generation
