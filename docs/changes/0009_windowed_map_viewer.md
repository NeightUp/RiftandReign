# Step 0009 - Windowed Map Viewer

## Step Name

Windowed debug viewer for the deterministic map pipeline.

## Purpose

Add a real desktop window that renders the current generated map as pointy-top hexes so the existing deterministic pipeline can be inspected visually without adding gameplay systems or changing map-generation behavior.

## Files Changed Or Created

- `README.md`
- `CHANGELOG.md`
- `docs/data_model.md`
- `docs/dev_workflow.md`
- `docs/generator_pipeline.md`
- `docs/map_spec.md`
- `docs/repo_index.md`
- `docs/changes/0009_windowed_map_viewer.md`
- `pyproject.toml`
- `src/rnr_mapgen/cli.py`
- `src/rnr_mapgen/colors.py`
- `src/rnr_mapgen/main.py`
- `src/rnr_mapgen/types.py`
- `src/rnr_mapgen/viewer.py`
- `tests/test_cli.py`
- `tests/test_colors.py`
- `tests/test_viewer.py`

## Important Decisions Made

- The viewer is launched with a dedicated `--view` flag so existing text-mode CLI behavior remains intact by default.
- `pygame` was chosen as the runtime windowing layer because it is small, practical, and sufficient for a debug-only viewer.
- Viewer launch state is kept outside `GeneratorConfig` so generation parameters remain focused on deterministic map output rather than presentation mode.
- The viewer consumes the same generated `MapData` produced by the existing CLI pipeline: board creation, scalar fields, terrain, hydrology, biomes, and start suitability.
- Hex rendering uses explicit pointy-top axial geometry with helper functions for world-space placement, screen transforms, and screen-to-hex hover lookup.
- Tile colors stay intentionally flat and debug-oriented: water, plains, forest, desert, tundra, hills, and mountains each use distinct colors, and rivers render as a simple overlay.

## Assumptions Made

- A lightweight debug window is more valuable at this stage than a larger retained-mode UI framework.
- Basic panning and zoom are sufficient for inspecting larger maps without adding selection systems or gameplay interaction.
- A compact hover readout is acceptable because it only exposes already-generated map data and does not introduce new mechanics.

## Work Intentionally Deferred

- units
- cities
- player turns
- selection systems beyond hover inspection
- fog of war
- east or west cylindrical wrapping
- polar ice or boundary treatment
- map-type presets
- final tile art layers
- gameplay mechanics of any kind
- exhaustive GUI event-loop testing
