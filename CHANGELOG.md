# Changelog

This file records the high-level history of meaningful repository changes. Detailed step notes live in `docs/changes/`.

## Step 0001 - Initial Scaffold

- Established the initial Python package layout under `src/rnr_mapgen/`.
- Added tested pointy-top axial and cube hex coordinate utilities.
- Added foundational project docs covering scope, map spec, pipeline, data model, acceptance criteria, and repository navigation.
- Added project tracking files: this changelog, `docs/repo_index.md`, and `docs/changes/0001_initial_scaffold.md`.
- Added a minimal executable entry point and focused pytest coverage for hex math.

## Step 0002 - Board Foundation

- Added a deterministic finite board builder that creates row-major pointy-top axial tiles from width, height, and seed configuration.
- Expanded the map data layer with validated config dimensions, tile-count helpers, and placeholder tile population for the full board.
- Updated the CLI to build an empty map and print a concise debug-oriented board summary.
- Added focused pytest coverage for board construction behavior and determinism.
- Updated repository tracking and navigation docs for the new board layer.
