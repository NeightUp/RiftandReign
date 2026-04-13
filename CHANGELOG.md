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

## Step 0005 - First-Pass Hydrology

- Added deterministic downhill routing, flow accumulation, and sparse first-pass river marking for land tiles.
- Updated the CLI to include river counts, maximum river strength, and river markers in the ASCII preview.
- Corrected PowerShell activation examples to use `.\.venv\Scripts\Activate.ps1` in repository workflow docs.
- Added focused pytest coverage for hydrology determinism, downhill routing, river placement constraints, and ASCII preview shape.
- Updated repository tracking and navigation docs for the new hydrology layer.

## Step 0006 - First-Pass Biomes

- Added deterministic first-pass biome classification for land tiles using explicit temperature, moisture, elevation, and light river-support rules.
- Updated the CLI to include biome counts and a biome-aware ASCII preview.
- Added focused pytest coverage for biome determinism, land coverage, water handling, metadata preservation, biome diversity, and preview shape.
- Updated repository tracking and navigation docs for the new biome layer while preserving the Windows PowerShell workflow.

## Step 0007 - Start Suitability

- Added deterministic first-pass start suitability scoring for land tiles with explicit land-neighborhood, biome, river, edge, and cramped-terrain rules.
- Added deterministic top-candidate selection for likely player starts without placing players yet.
- Updated the CLI to include start-eligible counts and top start candidate summaries alongside the existing biome preview.
- Added focused pytest coverage for start scoring determinism, candidate filtering, ordering stability, and data preservation.
- Updated repository tracking and navigation docs for the new start-suitability layer.

## Step 0008 - CLI Config And Larger Maps

- Added standard-library CLI argument parsing for width, height, seed, sea level, river source threshold, and ASCII preview limits.
- Increased the default CLI map size to a more useful testing baseline while keeping output manageable through deterministic preview clipping.
- Routed terrain and hydrology threshold configuration through `GeneratorConfig`.
- Added focused pytest coverage for CLI parsing, validation, larger-map stability, deterministic preview behavior, and full-pipeline config preservation.
- Updated repository tracking and navigation docs for the new configurable map workflow.

## Step 0009 - Windowed Map Viewer

- Added an optional `--view` CLI mode that opens a lightweight pointy-top hex debug viewer for the same deterministic generated map used by the text summary path.
- Added flat debug biome and water colors plus simple river overlays, panning, zoom, and compact hover inspection for map-focused visual debugging.
- Kept the existing CLI generation pipeline and text summary behavior intact when `--view` is not used.
- Added focused pytest coverage for `--view` parsing, viewer geometry helpers, and biome color mapping.
- Updated repository docs and detailed step history for the new windowed debug-viewer layer.

## Step 0010 - Rectangular World And Continent Overhaul

- Added a rectangular odd-row staggered display layout so the viewer and user-facing map dimensions read as a world strip instead of a slanted rhombus.
- Reworked elevation shaping to use deterministic broad continent centers, low-frequency macro fields, ocean breaks, and mild ocean-edge pressure instead of a simple center-biased land blob.
- Updated terrain cleanup to preserve coherent continents and oceans while removing tiny fragments, small inland ponds, and narrow low-elevation land bridges.
- Kept the existing CLI, debug viewer, hydrology, biome, and start-suitability workflow intact while retuning them to consume the new world shape.
- Added focused pytest coverage for layout round-tripping, viewer stagger behavior, practical land ratios, and multi-region large-map terrain behavior.
