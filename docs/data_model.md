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

For the current scalar-field step:

- `elevation` is a normalized scalar field, not final terrain classification
- `moisture` is a normalized scalar field, not a biome result
- `temperature` is a normalized scalar field, not a climate-zone label

For the current terrain-classification step:

- `is_water` is populated by the first-pass terrain classifier
- `elevation`, `moisture`, and `temperature` remain available for later systems

For the current hydrology step:

- `river_flow_to` stores the first-pass downhill outflow target when one exists
- `flow_accumulation` stores simple upstream contribution for land routing
- `has_river` marks tiles selected as first-pass river carriers
- `river_strength` stores a lightweight derived river magnitude
- lake, biome, and start-suitability fields remain placeholders

## MapData

`MapData` represents the generated map as a whole.

- width
- height
- seed used for generation
- configuration used for generation
- mapping from `HexCoord` to `TileData`

For the current board-foundation step, `MapData` stores a finite non-wrapping rectangular playable field generated in row-major order with:

- `q` spanning `0..width-1`
- `r` spanning `0..height-1`

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

For the current finite board, neighbors outside the rectangular playable field are simply absent from `MapData.tiles`. There is no wraparound behavior.
