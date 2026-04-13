# Repository Index

This is the authoritative navigation file for the repository. Read this file first when reviewing the project on GitHub.

## Project Purpose

`RiftandReign` currently exists to provide the foundation for a deterministic map generator for a hex-based 4X strategy game. The current implementation is intentionally minimal: project scaffold, documentation, change tracking, core data structures, a finite board layer, deterministic scalar fields, a first-pass land and water classifier, first-pass hydrology groundwork, first-pass biome classification, first-pass start suitability scoring, configurable CLI-driven map generation, a lightweight windowed debug viewer, and tested hex-grid math. Final start placement and later pipeline refinements are still not implemented.

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
13. `docs/changes/0004_land_water_classification.md`
14. `docs/changes/0005_first_pass_hydrology.md`
15. `docs/changes/0006_first_pass_biomes.md`
16. `docs/changes/0007_start_suitability.md`
17. `docs/changes/0008_cli_config_and_larger_maps.md`
18. `docs/changes/0009_windowed_map_viewer.md`

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
|       +-- 0003_scalar_fields.md
|       +-- 0004_land_water_classification.md
|       +-- 0005_first_pass_hydrology.md
|       +-- 0006_first_pass_biomes.md
|       +-- 0007_start_suitability.md
|       `-- 0008_cli_config_and_larger_maps.md
+-- pyproject.toml
+-- src/
|   `-- rnr_mapgen/
|       +-- __init__.py
|       +-- __main__.py
|       +-- board.py
|       +-- biomes.py
|       +-- colors.py
|       +-- fields.py
|       +-- hydrology.py
|       +-- hex.py
|       +-- cli.py
|       +-- main.py
|       +-- starts.py
|       +-- terrain.py
|       +-- types.py
|       `-- viewer.py
`-- tests/
    +-- test_board.py
    +-- test_biomes.py
    +-- test_fields.py
    +-- test_hydrology.py
    +-- test_cli.py
    +-- test_colors.py
    +-- test_starts.py
    +-- test_terrain.py
    +-- test_hex.py
    `-- test_viewer.py
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
- `docs/changes/0004_land_water_classification.md`
  Purpose: detailed historical record for the first-pass land and water classification step.
- `docs/changes/0005_first_pass_hydrology.md`
  Purpose: detailed historical record for the first-pass hydrology groundwork step.
- `docs/changes/0006_first_pass_biomes.md`
  Purpose: detailed historical record for the first-pass biome classification step.
- `docs/changes/0007_start_suitability.md`
  Purpose: detailed historical record for the first-pass start suitability scoring step.
- `docs/changes/0008_cli_config_and_larger_maps.md`
  Purpose: detailed historical record for the configurable CLI and larger-map workflow step.
- `docs/changes/0009_windowed_map_viewer.md`
  Purpose: detailed historical record for the windowed debug-viewer step.
- `src/rnr_mapgen/__init__.py`
  Purpose: minimal package initialization and version export.
- `src/rnr_mapgen/__main__.py`
  Purpose: module execution support for `python -m rnr_mapgen`.
- `src/rnr_mapgen/board.py`
  Purpose: deterministic finite board construction.
- `src/rnr_mapgen/biomes.py`
  Purpose: deterministic first-pass land-biome classification and biome-aware ASCII preview helpers.
- `src/rnr_mapgen/cli.py`
  Purpose: standard-library CLI parsing for map-focused configuration, preview controls, and optional windowed debug-viewer launch.
- `src/rnr_mapgen/colors.py`
  Purpose: flat debug color mapping for water, first-pass land biomes, and viewer UI accents.
- `src/rnr_mapgen/fields.py`
  Purpose: deterministic scalar-field generation for elevation, moisture, and temperature.
- `src/rnr_mapgen/hydrology.py`
  Purpose: deterministic downhill routing, flow accumulation, river marking, and river-aware ASCII preview helpers.
- `src/rnr_mapgen/main.py`
  Purpose: executable entry point that builds the board, applies scalar fields, classifies terrain, adds hydrology groundwork, assigns first-pass biomes, scores start suitability, and either prints a concise debug summary or launches the windowed viewer.
- `src/rnr_mapgen/starts.py`
  Purpose: deterministic start suitability scoring and top-candidate selection helpers.
- `src/rnr_mapgen/terrain.py`
  Purpose: deterministic first-pass land and water classification plus ASCII terrain preview helpers.
- `src/rnr_mapgen/hex.py`
  Purpose: pointy-top axial and cube hex coordinate helpers used by future generator logic.
- `src/rnr_mapgen/types.py`
  Purpose: lightweight dataclasses for generator config, map-level tile data, and viewer launch state.
- `src/rnr_mapgen/viewer.py`
  Purpose: compact pointy-top hex debug viewer with panning, zoom, hover inspection, and simple river overlays.
- `tests/test_board.py`
  Purpose: focused pytest coverage for deterministic board construction and metadata preservation.
- `tests/test_biomes.py`
  Purpose: focused pytest coverage for biome determinism, land coverage, metadata preservation, biome diversity, and ASCII preview shape.
- `tests/test_cli.py`
  Purpose: focused pytest coverage for CLI parsing, config validation, optional viewer launch flag, larger-map stability, and deterministic preview behavior.
- `tests/test_colors.py`
  Purpose: focused pytest coverage for flat debug biome and water color mapping.
- `tests/test_fields.py`
  Purpose: focused pytest coverage for scalar-field determinism, value ranges, and metadata preservation.
- `tests/test_hydrology.py`
  Purpose: focused pytest coverage for hydrology determinism, downhill routing, river placement constraints, and ASCII preview shape.
- `tests/test_starts.py`
  Purpose: focused pytest coverage for start suitability determinism, candidate filtering, ordering stability, and data preservation.
- `tests/test_terrain.py`
  Purpose: focused pytest coverage for terrain determinism, land and water layout, metadata preservation, and ASCII preview shape.
- `tests/test_hex.py`
  Purpose: focused pytest coverage for the hex-grid utilities.
- `tests/test_viewer.py`
  Purpose: focused pytest coverage for pointy-top viewer geometry, coordinate conversion, and map-bounds helpers.
- `assets/`
  Purpose: pre-existing repository art assets. These are present in the repository tree but are not part of this scaffold implementation step.

## Entry Points

- Console script: `rnr-mapgen`
- Python module entry: `python -m rnr_mapgen`
- Callable function: `rnr_mapgen.main:main`

## Test Locations

- Automated tests live in `tests/`
- Board tests: `tests/test_board.py`
- Biome tests: `tests/test_biomes.py`
- CLI tests: `tests/test_cli.py`
- Field tests: `tests/test_fields.py`
- Hydrology tests: `tests/test_hydrology.py`
- Start tests: `tests/test_starts.py`
- Terrain tests: `tests/test_terrain.py`
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
- deterministic first-pass land and water classification
- deterministic first-pass downhill routing and sparse river marking
- deterministic first-pass land-biome classification
- deterministic first-pass start suitability scoring
- configurable CLI-driven map generation for larger deterministic maps
- lightweight windowed debug viewing of the current generated map
- lightweight map-related dataclasses
- debug-oriented CLI terrain, river, biome, and start summary with ASCII preview
- repository documentation and project tracking
- focused unit tests for hex utilities, board construction, scalar fields, terrain classification, hydrology, biomes, start suitability, CLI config, viewer geometry, and debug color mapping

Not implemented yet:

- wrapping
- lake-system simulation
- polar treatment
- fog of war
- map-type generation presets
- climate zoning beyond scalar groundwork
- final multi-player start placement
- start-region validation logic
- polished visualization beyond the current debug viewer

## Maintenance Rules

Future meaningful changes must also update:

- `docs/repo_index.md`
- `CHANGELOG.md`
- a new detailed file in `docs/changes/` when the change batch is substantial
