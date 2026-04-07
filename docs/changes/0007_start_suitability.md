# Step 0007 - Start Suitability

## Step Name

Deterministic first-pass start suitability scoring.

## Purpose

Add a first-pass notion of likely player-start quality by assigning deterministic suitability scores to land tiles, marking likely candidates, and exposing top candidate summaries in the CLI without attempting final multi-player placement.

## Files Changed Or Created

- `README.md`
- `CHANGELOG.md`
- `docs/acceptance_tests.md`
- `docs/data_model.md`
- `docs/generator_pipeline.md`
- `docs/map_spec.md`
- `docs/repo_index.md`
- `docs/changes/0007_start_suitability.md`
- `src/rnr_mapgen/main.py`
- `src/rnr_mapgen/starts.py`
- `src/rnr_mapgen/types.py`
- `tests/test_starts.py`

## Important Decisions Made

- Water tiles and mountains are hard-rejected as start candidates.
- Start suitability is driven by a small-radius neighborhood score with explicit rewards for nearby land, plains, forest, river access, and biome variety.
- The scoring pass also applies simple edge and cramped-terrain penalties to avoid obviously poor starts.
- Candidate ordering is deterministic and uses score first, then coordinate tie-breakers.
- The CLI now reports start-eligible tile counts and the top scored candidate coordinates instead of placing players.

## Assumptions Made

- A practical start heuristic is more useful at this stage than a full placement solver.
- Nearby plains and forest are reasonable first-pass proxies for productive expansion land.
- A small biome-variety reward helps identify flexible starts without requiring a full resource system.

## Work Intentionally Deferred

- final multi-player start placement
- resource spawning
- luxury or strategic balance systems
- faction-specific start logic
- rendering, GUI, or external visualization frameworks
- any gameplay systems outside map generation
