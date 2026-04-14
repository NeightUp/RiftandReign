# Step 0011 - Generator Reset Continents And Rivers

## Step Name

Generator reset for continent-first geography and selected river systems.

## Purpose

Replace the previous terrain and hydrology internals with a more standard continent-first world generator while preserving the existing CLI, text summary, and windowed debug viewer workflow. This step is specifically about recovering believable macro geography and river behavior without adding gameplay systems.

## Files Changed Or Created

- `README.md`
- `CHANGELOG.md`
- `docs/data_model.md`
- `docs/generator_pipeline.md`
- `docs/map_spec.md`
- `docs/repo_index.md`
- `docs/changes/0011_generator_reset_continents_and_rivers.md`
- `src/rnr_mapgen/fields.py`
- `src/rnr_mapgen/hydrology.py`
- `src/rnr_mapgen/noise.py`
- `src/rnr_mapgen/terrain.py`
- `src/rnr_mapgen/domain/models.py`
- `src/rnr_mapgen/generation/pipeline.py`
- `src/rnr_mapgen/application/cli.py`
- `src/rnr_mapgen/rendering/viewer.py`
- `tests/test_hydrology.py`
- `tests/test_terrain.py`
- `tests/test_viewer.py`
- `tests/test_cli.py`

## Important Decisions Made

- Macro terrain generation was reset around continent-first world shaping rather than incremental scalar-threshold tuning.
- The field pass now builds continent potential from deterministic continent clusters, island groups, basin breakers, and a preferred north-south ocean seam rather than allowing land to wrap around the display seam arbitrarily.
- Terrain classification now chooses a practical land ratio first, cleans the resulting landmask into usable continents and oceans, assigns broad water classes, and only then derives final elevation from continent structure, ruggedness, and inland uplift.
- A later correction pass backed out an over-strong seam and directional-field experiment after it produced striped worlds.
- The follow-up macro pass now keeps continent silhouette generation bounded by explicit continent regions, then reopens the preferred seam as a true ocean corridor during terrain cleanup and splits oversized supercontinents at weak saddles when one landmass dominates the world.
- Hydrology uses exactly one deterministic downhill receiver per land tile, which keeps the drainage graph tree-shaped and prevents inland visible-river bifurcation.
- Visible rivers are promoted from the drainage graph by weighted runoff accumulation and adaptive thresholds, so the viewer shows selected channels instead of the full drainage mesh.
- A further realism pass replaced bounded continent slabs with organic continent blob chains, added ocean-gap island groups, relaxed cleanup that was deleting too much land, and shifted ruggedness toward explicit ridge chains.
- Visible river selection now begins from major mouths and traces upstream tributaries, which produces cleaner main stems and fewer shallow drainage-looking paths.
- Biome assignment now uses water distance and surrounding terrain influence in addition to scalar climate values so the map does not read as simple latitude striping.
- The existing CLI surface and debug viewer were preserved, including `--view`, text summaries, preview clipping, and Windows PowerShell workflow commands.
- The codebase now has explicit `domain`, `generation`, `rendering`, and `application` layers, with top-level compatibility wrappers kept in place for a gradual transition.

## Assumptions Made

- A practical default land ratio for this debug-world style should stay near the middle of the range rather than chasing extreme ocean or land-heavy outputs.
- It is acceptable for some small maps to show sparse or no visible rivers as long as larger default-style maps produce meaningful promoted river systems.
- Coastline realism and river-network hierarchy matter more at this step than exposing many generator-tuning controls.
- The existing `river_source_threshold` CLI option should remain available and act as a minimum visible-channel promotion floor rather than forcing the old hydrology model.
- The preferred map style should usually produce 2-4 continent-scale landmasses plus smaller islands, with one major ocean seam available for display orientation.

## Work Intentionally Deferred

- east or west cylindrical wrapping
- polar treatment
- fog of war
- map-type presets
- final tile art layers
- final multiplayer start placement
- lake simulation and basin filling
- cities
- units
- gameplay mechanics of any kind
- manual GUI inspection tests
