# Repository Index

This is the authoritative navigation file for the repository. Read this file first when reviewing the project on GitHub.

## Project Purpose

`RiftandReign` currently exists to provide the foundation for a deterministic map generator for a hex-based 4X strategy game. The current implementation is intentionally minimal: project scaffold, documentation, change tracking, core data structures, and tested hex-grid math. The actual terrain-generation pipeline is documented but not yet implemented.

## Recommended Reading Order

1. `README.md`
2. `docs/repo_index.md`
3. `docs/project_scope.md`
4. `docs/map_spec.md`
5. `docs/generator_pipeline.md`
6. `docs/data_model.md`
7. `docs/acceptance_tests.md`
8. `CHANGELOG.md`
9. `docs/changes/0001_initial_scaffold.md`

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
|   +-- generator_pipeline.md
|   +-- map_spec.md
|   +-- project_scope.md
|   +-- repo_index.md
|   `-- changes/
|       `-- 0001_initial_scaffold.md
+-- pyproject.toml
+-- src/
|   `-- rnr_mapgen/
|       +-- __init__.py
|       +-- __main__.py
|       +-- hex.py
|       +-- main.py
|       `-- types.py
`-- tests/
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
- `src/rnr_mapgen/__init__.py`
  Purpose: minimal package initialization and version export.
- `src/rnr_mapgen/__main__.py`
  Purpose: module execution support for `python -m rnr_mapgen`.
- `src/rnr_mapgen/main.py`
  Purpose: current executable entry point for the scaffold package.
- `src/rnr_mapgen/hex.py`
  Purpose: pointy-top axial and cube hex coordinate helpers used by future generator logic.
- `src/rnr_mapgen/types.py`
  Purpose: lightweight dataclasses for config and map-level tile data.
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
- Current test file: `tests/test_hex.py`

## Documentation Locations

- Repository navigation: `docs/repo_index.md`
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
- lightweight map-related dataclasses
- repository documentation and project tracking
- focused unit tests for hex utilities

Not implemented yet:

- scalar field generation
- terrain generation
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
