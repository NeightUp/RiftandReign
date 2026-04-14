# Generator Pipeline

The generator is planned as a deterministic layered pipeline rather than a single monolithic function. Each stage should consume clearly defined inputs and produce data that later stages can inspect, validate, and debug.

## 1. Seed And Config

- Inputs: external seed value, generator configuration
- Outputs: deterministic random context and normalized configuration values
- Purpose: establish reproducibility and the parameters that drive every later stage

## 2. Base Scalar Fields

- Inputs: seed context, map dimensions, configuration
- Outputs: scalar fields such as continentality, roughness, moisture tendency, and temperature tendency
- Purpose: create the continuous underlying signals from which terrain and climate can later be derived

Current implementation note:

- the repository now assigns deterministic normalized scalar values for elevation, moisture, and temperature to every tile
- elevation now uses broad continent centers, secondary landmass seeds, low-frequency macro noise, inland ocean breaks, and latitude-independent macro shaping instead of a simple center bias
- these are groundwork fields only and are not yet land or water decisions, hydrology, climate zoning, or biome classification

Current configuration note:

- the CLI now exposes explicit width, height, seed, sea level, river source threshold, and preview-size arguments
- the same CLI arguments produce the same generated map summary and preview

## 3. Landmask And Elevation

- Inputs: base scalar fields, configuration thresholds
- Outputs: land or water classification and elevation values per hex
- Purpose: form coastlines, landmasses, basins, and highlands that define the macro terrain layout

Current implementation note:

- the repository now performs a continent-oriented deterministic land and water classification from the scalar-field layer
- the current classifier uses elevation plus local coherence cleanup and narrow-bridge removal so the map reads more like continents, subcontinents, and ocean basins than a central land blob

## 4. Hydrology

- Inputs: elevation, landmask, potential water flow rules
- Outputs: drainage paths, river data, and lake flags where required
- Purpose: route water downhill in a consistent way and create plausible river systems tied to terrain

Current implementation note:

- the repository now computes deterministic downhill outflow targets for land tiles, including coherent coastal termination when rivers reach adjacent water
- weighted flow accumulation and adaptive channel selection are used to promote only significant drainage paths into visible rivers
- basin filling, lake simulation, and refined hydrology behavior are intentionally deferred

## 5. Climate

- Inputs: elevation, moisture-related data, temperature-related data, water proximity
- Outputs: tile moisture and tile temperature values
- Purpose: translate terrain and field data into climate values that can drive biome assignment

## 6. Biome Classification

- Inputs: land or water classification, temperature, moisture, elevation, hydrology markers
- Outputs: biome value for every tile
- Purpose: convert raw environmental data into terrain categories that are usable by downstream game systems

Current implementation note:

- the repository now assigns a compact first-pass land-biome set from scalar fields, elevation, and light river support
- this pass is intentionally simple and is meant as a readable world layer rather than a final biome system

## 7. Start-Region Validation

- Inputs: full tile map, terrain outputs, suitability metadata
- Outputs: validated starting-region assessments and reject or accept signals for the map
- Purpose: ensure generated maps have regions that are practical for expansion and later gameplay

Current implementation note:

- the repository now computes first-pass per-tile start suitability scores and marks likely candidates
- final multi-player placement and full validation rules are still intentionally deferred

## 8. Debug Output

- Inputs: complete map data and intermediate layers
- Outputs: debug-friendly summaries or visualizations of the generated layers
- Purpose: make it possible to inspect failures, tune parameters, and audit deterministic behavior

Current implementation note:

- the repository now supports two debug-output paths from the same deterministic pipeline: the existing text summary plus ASCII preview, and an optional windowed viewer launched with `--view`
- the windowed viewer renders a rectangular odd-row staggered field of pointy-top hexes with flat biome and water colors, simple river overlays, panning, zoom, and a compact hover readout

## Why Build In Layers

Layering keeps the generator understandable and testable. Each stage can be validated independently, failures can be traced to a specific layer, and deterministic debugging becomes much easier than with one giant generator that mixes terrain, rivers, climate, and validation in a single pass.
