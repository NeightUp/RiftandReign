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

## Step 0003 - Scalar Fields

- Added deterministic scalar-field generation for elevation, moisture, and temperature on every tile.
- Updated the CLI to build the board, apply scalar fields, and print concise range and sample-value summaries.
- Added Windows-focused local development workflow documentation using the repository virtual environment and `python` commands.
- Added focused pytest coverage for scalar-field determinism, range guarantees, and metadata preservation.
- Updated repository tracking and navigation docs for the new workflow and scalar-field layer.

## Step 0004 - Land And Water Classification

- Added a deterministic first-pass terrain classifier that marks every tile as land or water using elevation-driven rules with light coherence cleanup.
- Added an ASCII terrain preview and expanded the CLI summary with land and water counts, percentages, and retained scalar ranges.
- Added focused pytest coverage for terrain determinism, land and water population, layout changes across seeds, metadata preservation, and ASCII preview shape.
- Updated repository docs and step history for the new terrain-classification layer while keeping the Windows `.venv` plus `python` workflow intact.
