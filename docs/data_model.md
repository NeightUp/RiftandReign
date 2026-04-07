# Data Model

This document defines the core project data model for the map generator foundation.

## HexCoord

`HexCoord` is the primary coordinate type for storage and public interfaces.

- fields: axial `q`, `r`
- role: identify a macro hex tile in a pointy-top axial grid
- expectations: supports conversion to cube form, neighbor lookup, and distance calculations

## CubeCoord

`CubeCoord` is a helper form used for algorithms.

- fields: `x`, `y`, `z`
- invariant: `x + y + z == 0`
- role: simplify distance and some traversal logic

Storage should remain axial unless an algorithm benefits from temporary cube conversion.

## TileData

`TileData` represents the generated state for a single macro hex tile.

Expected fields are intentionally minimal for now:

- `coord`
- `elevation`
- `is_water`
- `moisture`
- `temperature`
- `biome`
- `river_flow_to`
- `is_lake`
- `start_suitability`

Some fields may remain placeholders until the corresponding pipeline stages are implemented.

## MapData

`MapData` represents the generated map as a whole.

- dimensions or generation bounds
- seed used for generation
- configuration used for generation
- mapping from `HexCoord` to `TileData`

This structure should support deterministic generation, inspection, and later debug output.

## GeneratorConfig

`GeneratorConfig` carries the generator parameters that shape output.

At minimum it should describe:

- map width
- map height
- seed

It may later expand with terrain-tuning values, but should remain explicit and serializable.

## Neighbor Logic Expectations

The repository uses pointy-top axial coordinates. Neighbor logic should therefore follow the standard six axial offsets for pointy-top hexes. Utilities should expose direct neighbor lookup and a way to list all six neighbors from a coordinate.

Algorithm-facing helpers may convert to cube coordinates internally, but storage and public-facing interfaces remain axial.
