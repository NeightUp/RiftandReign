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
- these are groundwork fields only and are not yet land or water decisions, hydrology, climate zoning, or biome classification

## 3. Landmask And Elevation

- Inputs: base scalar fields, configuration thresholds
- Outputs: land or water classification and elevation values per hex
- Purpose: form coastlines, landmasses, basins, and highlands that define the macro terrain layout

## 4. Hydrology

- Inputs: elevation, landmask, potential water flow rules
- Outputs: drainage paths, river data, and lake flags where required
- Purpose: route water downhill in a consistent way and create plausible river systems tied to terrain

## 5. Climate

- Inputs: elevation, moisture-related data, temperature-related data, water proximity
- Outputs: tile moisture and tile temperature values
- Purpose: translate terrain and field data into climate values that can drive biome assignment

## 6. Biome Classification

- Inputs: land or water classification, temperature, moisture, elevation, hydrology markers
- Outputs: biome value for every tile
- Purpose: convert raw environmental data into terrain categories that are usable by downstream game systems

## 7. Start-Region Validation

- Inputs: full tile map, terrain outputs, suitability metadata
- Outputs: validated starting-region assessments and reject or accept signals for the map
- Purpose: ensure generated maps have regions that are practical for expansion and later gameplay

## 8. Debug Output

- Inputs: complete map data and intermediate layers
- Outputs: debug-friendly summaries or visualizations of the generated layers
- Purpose: make it possible to inspect failures, tune parameters, and audit deterministic behavior

## Why Build In Layers

Layering keeps the generator understandable and testable. Each stage can be validated independently, failures can be traced to a specific layer, and deterministic debugging becomes much easier than with one giant generator that mixes terrain, rivers, climate, and validation in a single pass.
