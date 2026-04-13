# Step 0008 - CLI Config And Larger Maps

## Step Name

Configurable CLI workflow for larger deterministic maps.

## Purpose

Make the map generator more useful for real evaluation by allowing width, height, seed, and a few existing tuning controls to be supplied from the command line, while keeping output readable for larger maps through deterministic ASCII preview clipping.

## Files Changed Or Created

- `README.md`
- `CHANGELOG.md`
- `docs/acceptance_tests.md`
- `docs/data_model.md`
- `docs/generator_pipeline.md`
- `docs/map_spec.md`
- `docs/repo_index.md`
- `docs/changes/0008_cli_config_and_larger_maps.md`
- `src/rnr_mapgen/biomes.py`
- `src/rnr_mapgen/cli.py`
- `src/rnr_mapgen/hydrology.py`
- `src/rnr_mapgen/main.py`
- `src/rnr_mapgen/starts.py`
- `src/rnr_mapgen/terrain.py`
- `src/rnr_mapgen/types.py`
- `tests/test_cli.py`

## Important Decisions Made

- CLI parsing uses the standard library `argparse` module and remains map-focused only.
- `GeneratorConfig` now carries a small set of practical CLI-facing controls: width, height, seed, sea level threshold, river source threshold, and preview width or height.
- The default CLI map size was increased to a more useful baseline for evaluation.
- Large previews are clipped deterministically using a top-left crop rather than attempting to print the full map.
- Terrain and hydrology now read their main thresholds from `GeneratorConfig` instead of only from module constants.

## Assumptions Made

- Top-left clipping is sufficient for repeatable terminal debugging at this stage.
- Width, height, and seed are the essential controls; sea level and river source threshold are the most useful optional tuning knobs already supported by the current pipeline.
- Preview-size controls belong in the config because they materially affect CLI debug output and testability.

## Work Intentionally Deferred

- wrapping
- polar treatment
- fog of war
- map-type generation presets beyond future scaffolding
- gameplay mechanics of any kind
- rendering, GUI, or external visualization frameworks
