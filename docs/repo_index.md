# Repository Index

This is the authoritative navigation file for the repository. Read this file first when reviewing the project on GitHub.

## Project Purpose

`RiftandReign` currently exists to provide the foundation for a deterministic map generator for a hex-based 4X strategy game. The current implementation is intentionally minimal: project scaffold, documentation, change tracking, core data structures, a finite board layer, deterministic scalar fields, and tested hex-grid math. Terrain classification and later pipeline stages are still not implemented.

## Recommended Reading Order

1. `README.md`
2. `docs/repo_index.md`
3. `docs/dev_workflow.md`
4. `docs/project_scope.md`
5. `docs/map_spec.md`
6. `docs/generator_pipeline.md`
7. `docs/data_model.md`
8. `docs/acceptance_tests.md`
9. `CHANGELOG.md`
10. `docs/changes/0001_initial_scaffold.md`
11. `docs/changes/0002_board_foundation.md`
12. `docs/changes/0003_scalar_fields.md`

## Current Top-Level Structure

```text
RiftandReign/
+-- CHANGELOG.md
+-- README.md
+-- assets/
|   +-- city/
|   +-- map/
|   `-- units/
+-- docs/
|   +-- acceptance_tests.md
|   +-- data_model.md
|   +-- dev_workflow.md
|   +-- generator_pipeline.md
|   +-- map_spec.md
|   +-- project_scope.md
|   +-- repo_index.md
|   `-- changes/
|       +-- 0001_initial_scaffold.md
|       +-- 0002_board_foundation.md
|       `-- 0003_scalar_fields.md
+-- pyproject.toml
+-- src/
|   `-- rnr_mapgen/
|       +-- __init__.py
|       +-- __main__.py
|       +-- board.py
|       +-- fields.py
|       +-- hex.py
|       +-- main.py
|       `-- types.py
`-- tests/
    +-- test_board.py
    +-- test_fields.py
    `-- test_hex.py
```

## Important Files And Paths

- `README.md`
  Purpose: top-level overview, current scope boundaries, setup, run, and test instructions.
- `pyproject.toml`
  Purpose: Python packaging, setuptools configuration, optional dev dependencies, and console entry point definition.
- `CHANGELOG.md`
  Purpose: concise high-level project history.
- `docs/project_scope.md`
  Purpose: authoritative description of what this repository is and is not building right now.
- `docs/dev_workflow.md`
  Purpose: Windows-focused local development workflow for the repository virtual environment and standard `python` commands.
- `docs/map_spec.md`
  Purpose: design-level specification for the intended v1 macro hex map output.
- `docs/generator_pipeline.md`
  Purpose: authoritative description of the planned layered deterministic generation pipeline.
- `docs/data_model.md`
  Purpose: authoritative description of the intended core coordinate and map data structures.
- `docs/acceptance_tests.md`
  Purpose: project-level acceptance criteria for the eventual completed generator.
- `docs/repo_index.md`
  Purpose: authoritative navigation file for reviewers and maintainers.
- `docs/changes/0001_initial_scaffold.md`
  Purpose: detailed historical record for the initial scaffold step.
- `docs/changes/0002_board_foundation.md`
  Purpose: detailed historical record for the deterministic board foundation step.
- `docs/changes/0003_scalar_fields.md`
  Purpose: detailed historical record for the scalar-field groundwork and workflow documentation step.
- `src/rnr_mapgen/__init__.py`
  Purpose: minimal package initialization and version export.
- `src/rnr_mapgen/__main__.py`
  Purpose: module execution support for `python -m rnr_mapgen`.
- `src/rnr_mapgen/board.py`
  Purpose: deterministic finite board construction.
- `src/rnr_mapgen/fields.py`
  Purpose: deterministic scalar-field generation and concise scalar summary formatting for CLI output.
- `src/rnr_mapgen/main.py`
  Purpose: executable entry point that builds the board, applies scalar fields, and prints a concise debug summary.
- `src/rnr_mapgen/hex.py`
  Purpose: pointy-top axial and cube hex coordinate helpers used by future generator logic.
- `src/rnr_mapgen/types.py`
  Purpose: lightweight dataclasses for generator config and map-level tile data.
- `tests/test_board.py`
  Purpose: focused pytest coverage for deterministic board construction and metadata preservation.
- `tests/test_fields.py`
  Purpose: focused pytest coverage for scalar-field determinism, value ranges, and metadata preservation.
- `tests/test_hex.py`
  Purpose: focused pytest coverage for the hex-grid utilities.
- `assets/`
  Purpose: pre-existing repository art assets. These are present in the repository tree but are not part of this scaffold implementation step.

## Entry Points

- Console script: `rnr-mapgen`
- Python module entry: `python -m rnr_mapgen`
- Callable function: `rnr_mapgen.main:main`

## Test Locations

- Automated tests live in `tests/`
- Board tests: `tests/test_board.py`
- Field tests: `tests/test_fields.py`
- Hex tests: `tests/test_hex.py`

## Documentation Locations

- Repository navigation: `docs/repo_index.md`
- Local development workflow: `docs/dev_workflow.md`
- Scope: `docs/project_scope.md`
- Map spec: `docs/map_spec.md`
- Pipeline: `docs/generator_pipeline.md`
- Data model: `docs/data_model.md`
- Acceptance criteria: `docs/acceptance_tests.md`

## Change History Locations

- Quick summary history: `CHANGELOG.md`
- Detailed step records: `docs/changes/`

## Authoritative Spec Files

The current authoritative files for scope and design intent are:

- `docs/project_scope.md`
- `docs/map_spec.md`
- `docs/generator_pipeline.md`
- `docs/data_model.md`
- `docs/acceptance_tests.md`

## Current Implementation Status

Implemented now:

- packaging and executable scaffold
- pointy-top hex coordinate math
- finite non-wrapping board creation
- deterministic scalar fields for elevation, moisture, and temperature
- lightweight map-related dataclasses
- debug-oriented CLI scalar-field summary
- repository documentation and project tracking
- focused unit tests for hex utilities, board construction, and scalar fields

Not implemented yet:

- terrain generation
- land and water classification
- hydrology
- climate
- biome classification
- start-region validation logic
- debug visualization output beyond documentation

## Maintenance Rules

Future meaningful changes must also update:

- `docs/repo_index.md`
- `CHANGELOG.md`
- a new detailed file in `docs/changes/` when the change batch is substantial
