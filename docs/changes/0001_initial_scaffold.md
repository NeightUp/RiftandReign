# Step 0001 - Initial Scaffold

## Step Name

Initial repository scaffold for the RiftandReign map generator.

## Purpose

Create the minimum professional foundation for the project before terrain-generation work begins. This step establishes package structure, repository navigation, durable project-tracking files, core data structures, and tested hex-grid math while intentionally avoiding any actual map-generation implementation.

## Files Created

- `README.md`
- `.gitignore`
- `pyproject.toml`
- `CHANGELOG.md`
- `docs/project_scope.md`
- `docs/map_spec.md`
- `docs/generator_pipeline.md`
- `docs/data_model.md`
- `docs/acceptance_tests.md`
- `docs/repo_index.md`
- `docs/changes/0001_initial_scaffold.md`
- `src/rnr_mapgen/__init__.py`
- `src/rnr_mapgen/__main__.py`
- `src/rnr_mapgen/main.py`
- `src/rnr_mapgen/hex.py`
- `src/rnr_mapgen/types.py`
- `tests/test_hex.py`

## Important Decisions Made

- The repository is explicitly scoped to the map generator only, not the broader game.
- Axial coordinates are the storage and interface format, with cube helpers used only for algorithm support.
- The map is defined as pointy-top, finite, and non-wrapping for v1.
- The future generator is documented as a deterministic layered pipeline rather than a monolithic process.
- Repository navigation and change history are treated as required maintenance artifacts from the first step.
- Existing `assets/` content is preserved but excluded from the implementation scope of this scaffold.

## Assumptions Made

- Python 3.11 or newer is acceptable as the project baseline.
- The existing `assets/` tree remains in the repository for future use, even though it is out of scope for this step.
- `start_suitability` is documented as a placeholder field rather than a finalized scoring model at this stage.

## Work Intentionally Deferred

- all actual map generation
- scalar field generation
- land and water assignment
- elevation modeling
- rivers and lakes logic
- climate modeling
- biome classification rules
- start-region validation implementation
- visualization beyond future debug-oriented outputs
- any gameplay systems outside the generator
