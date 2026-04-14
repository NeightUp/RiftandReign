# Project Scope

## Immediate Mission

This repository exists to build a deterministic map generator for a hex-based 4X strategy game. The current phase is limited to building a clean foundation: repository structure, coordinate math, core data structures, project documentation, and tracking files that make later work easy to audit from GitHub alone.

## In Scope

Current in-scope work includes:

- repository scaffold and packaging
- pointy-top hex math utilities
- deterministic map data structures
- documentation for the intended terrain-generation pipeline
- debug-oriented outputs and validation planning
- focused automated tests
- project tracking documentation and change history

## Out of Scope For Now

The following are intentionally excluded from this phase:

- full game systems
- economy
- units
- combat
- AI rivals
- cities and faction mechanics
- subhex gameplay
- art polish
- final UI or presentation layers
- speculative systems outside the map generator

## First Playable Map Milestone

The first playable map milestone is achieved when this repository can deterministically generate a macro hex map from a seed and configuration, using a rectangular world-strip presentation with cylindrical east or west generation behavior, with enough data on each tile to support terrain layout, rivers, climate, biome assignment, and basic starting-area validation for later game integration.

For that milestone, the generator should:

- produce the same map for the same seed and config
- produce usable macro-scale landmasses and coastlines
- assign hydrology and biome data to every tile
- expose data in a debug-friendly structure
- pass documented acceptance criteria
