# Step 0011 - Geography Realism And River Networks

## Step Name

Geography realism pass and river-network selection overhaul.

## Purpose

Improve the overall natural feel of generated maps by making macro land and ocean structure less synthetic, while replacing the previous overly dense river display with a more believable terrain-driven river network that promotes only significant drainage channels.

## Files Changed Or Created

- `README.md`
- `CHANGELOG.md`
- `docs/data_model.md`
- `docs/generator_pipeline.md`
- `docs/map_spec.md`
- `docs/repo_index.md`
- `docs/changes/0011_geography_realism_and_river_networks.md`
- `src/rnr_mapgen/fields.py`
- `src/rnr_mapgen/hydrology.py`
- `tests/test_hydrology.py`

## Important Decisions Made

- Macro elevation shaping was extended with secondary landmass seeds and additional coastal breakup so maps can support more plausible subcontinents and less uniform ocean voids.
- Hydrology still uses one deterministic downstream receiver per tile, which preserves a tree-like drainage structure and prevents inland river splitting.
- Visible rivers are now selected from the drainage network using weighted runoff accumulation and adaptive promotion thresholds instead of marking nearly every accumulated downhill segment.
- Coastal water tiles can now serve as coherent river termini while visible river tiles themselves remain land-only.
- River strength is now derived from selected channel significance rather than a simple scaled accumulation passthrough.

## Assumptions Made

- A debug viewer can still use simple river lines as long as the underlying selected channels are materially more hierarchical and less saturated.
- It is acceptable for different seeds to produce very different river density as long as the result is terrain-driven and remains within practical bounds.
- Interior sinks are still acceptable in this simplified model until lake simulation or basin filling is implemented in a later step.

## Work Intentionally Deferred

- lake simulation
- basin filling
- east or west cylindrical wrapping
- polar treatment
- fog of war
- map-type presets
- final tile art layers
- final multiplayer start placement
- cities
- units
- gameplay mechanics of any kind
- exhaustive GUI window-loop testing
