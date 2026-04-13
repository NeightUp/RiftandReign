# Step 0010 - Rectangular World And Continent Overhaul

## Step Name

Rectangular world presentation and continent-generation overhaul.

## Purpose

Fix the two largest structural problems in the current map pipeline: the viewer presenting the world as a slanted rhombus instead of a rectangular strip, and the terrain generator overproducing a central land blob instead of more believable continents and oceans.

## Files Changed Or Created

- `README.md`
- `CHANGELOG.md`
- `docs/data_model.md`
- `docs/generator_pipeline.md`
- `docs/map_spec.md`
- `docs/repo_index.md`
- `docs/changes/0010_rectangular_world_and_continent_overhaul.md`
- `src/rnr_mapgen/board.py`
- `src/rnr_mapgen/fields.py`
- `src/rnr_mapgen/hydrology.py`
- `src/rnr_mapgen/biomes.py`
- `src/rnr_mapgen/starts.py`
- `src/rnr_mapgen/terrain.py`
- `src/rnr_mapgen/types.py`
- `src/rnr_mapgen/viewer.py`
- `tests/test_board.py`
- `tests/test_colors.py`
- `tests/test_starts.py`
- `tests/test_terrain.py`
- `tests/test_viewer.py`

## Important Decisions Made

- Axial coordinates remain the algorithm-facing storage format for neighbor math and downstream systems.
- A separate odd-row staggered display layout was introduced so width and height still describe a rectangular world strip from the user’s perspective.
- Tile records now store both axial coordinates and rectangular display positions so rendering, previews, and user-facing inspection can stay clear without rewriting core hex math.
- Elevation shaping now uses deterministic broad continent centers, low-frequency macro noise, inland ocean-break centers, and rift-like ocean corridors instead of a simple center bias.
- Terrain cleanup now includes small-region cleanup, tiny inland-water filling, and narrow low-elevation land-bridge removal to reduce accidental supercontinent connectors.
- The existing conceptual pipeline was preserved: board, scalar fields, terrain, hydrology, biomes, starts, and debug output still run in the same order.

## Assumptions Made

- A rectangular odd-row display model is sufficient to make the viewer read like a strategy-game world strip without changing topology or adding wrapping.
- It is acceptable for some seeds to still produce a dominant continent as long as the default generator supports multiple major land regions on many larger-map seeds.
- First-pass biome and start-suitability heuristics can remain simple if they still behave sensibly on the new continent-oriented terrain layer.

## Work Intentionally Deferred

- east or west cylindrical wrapping
- polar ice or boundary treatment
- fog of war
- map-type presets
- final tile art layers
- final multiplayer start placement
- cities
- units
- gameplay mechanics of any kind
- exhaustive GUI window-loop testing
