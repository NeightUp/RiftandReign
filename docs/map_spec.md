# Map Specification

## V1 Design Intent

The intended v1 output is a macro-scale strategy map composed of pointy-top hexes. These are map-level gameplay tiles only. There is no subhex system in this repository at this stage.

## Geometry

- hex orientation: pointy-top
- coordinate storage and interface: axial coordinates `(q, r)`
- rectangular player-facing world presentation: odd-row staggered display layout
- algorithm helpers: cube-coordinate conversion where useful
- map topology: finite and non-wrapping

## Intended Tile-Level Outputs

Each generated hex should eventually expose at least the following data:

- coordinate
- elevation
- water or land classification
- moisture
- temperature
- biome
- river data
- lake flag where applicable
- start suitability metadata placeholder

## Desired Map Qualities

The generator should eventually aim for:

- interesting coastlines instead of uniform blobs
- meaningful land masses with navigable shapes
- plausible river placement driven by terrain
- biome variety that follows climate logic
- useful buildable land for expansion
- reasonable starting areas for later validation

Current implementation note:

- the repository now performs a first-pass deterministic land and water classification
- this pass is now continent-oriented and is intended to produce broad oceans, multiple large land regions on many seeds, secondary landmasses, and less artificial coastlines
- the repository now also performs terrain-driven flow accumulation and selected river-channel marking on land tiles
- the repository now assigns first-pass land biome labels for readable world-layer output
- the repository now assigns first-pass start suitability scores without placing players yet
- the repository now includes a debug-only windowed viewer that renders the current generated map as a rectangular staggered field of pointy-top hexes with flat terrain colors and selected river overlays

## Boundaries For This Repository

This repository currently concerns only macro hex map generation. It does not define tactical combat grids, subhex terrain detail, or final art/rendering systems.

For current debugging, large maps may be previewed with a deterministic cropped ASCII view or opened in a lightweight windowed debug viewer. The viewer is intentionally flat-colored and map-focused rather than a final presentation layer.
