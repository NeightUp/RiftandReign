# RiftandReign Map Generator

This repository contains the foundation for a deterministic map generator for a hex-based 4X strategy game. The current implementation includes tested pointy-top hex utilities, a continent-first macro geography pass, continent-derived elevation, basin-aware river-network hydrology, first-pass biome classification, first-pass start suitability scoring, configurable CLI-driven map generation, and a wrap-aware windowed debug viewer for inspecting the generated map.

The codebase is being reshaped toward a cleaner game-oriented structure:

- `rnr_mapgen.domain` for stable world and tile data models
- `rnr_mapgen.generation` for map generation and layout helpers
- `rnr_mapgen.rendering` for the current pygame-based viewer layer
- `rnr_mapgen.application` for CLI and application wiring

Top-level modules still exist as compatibility wrappers while that refactor continues.

The repository is focused on the map generator only. The intended long-term pipeline is:

1. seed and configuration
2. macro continent generation
3. land and water plus elevation
4. hydrology
5. climate
6. biome classification
7. validation
8. debug visualization

## Current Scope

In scope right now:

- repository scaffold and packaging
- deterministic project data structures
- pointy-top hex coordinate math
- finite rectangular board construction with a pointy-top display layout that is being prepared for cylindrical east/west wrapping
- deterministic macro continent shaping with a preferred ocean seam, 2-4 large landmasses, bounded continent regions, island groups, and latitude-aware world-strip behavior
- deterministic continent-first land and water classification plus continent-derived elevation and broad water classes
- broad water classes for coast, deep ocean, inland sea, and lake tiles
- deterministic basin-aware hydrology with downhill routing, flow accumulation, and selected visible river channels
- deterministic first-pass biome classification
- deterministic first-pass start suitability scoring
- configurable CLI-driven map generation for larger maps and seed testing
- debug-oriented CLI terrain, river, biome, and start summary with ASCII preview
- windowed pointy-top hex debug viewer with flat biome colors, river overlays, panning, zoom, and hover inspection
- documentation for scope, map spec, pipeline, and data model
- project tracking via changelog and detailed change notes
- focused tests

Out of scope right now:

- game systems
- cities, units, economy, combat, or AI
- subhex gameplay
- polished rendering or final UI

## Getting Started

Python 3.11+ is required.

Local Windows workflow:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
python -m pytest
python -m rnr_mapgen
rnr-mapgen
python -m rnr_mapgen --width 80 --height 40 --seed 5
rnr-mapgen --width 80 --height 40 --seed 123 --preview-width 32 --preview-height 16
python -m rnr_mapgen --view
rnr-mapgen --width 80 --height 40 --seed 123 --view
```

## Documentation

Start with [docs/repo_index.md](docs/repo_index.md). It is the authoritative navigation file for the repository and points to the scope, spec, pipeline, data model, workflow, tests, and change history.

## Current Status

The CLI now defaults to an `80x40` world and accepts explicit width, height, seed, sea level, river source threshold, and ASCII preview size. `--view` opens a pygame-based viewer that renders the same deterministic generated map as a pointy-top hex world strip, including wrap-aware horizontal rendering so east/west scrolling can evolve toward a cylindrical world presentation. The current world pass now builds continents from explicit bounded regions, keeps a reopened north-south ocean seam, splits oversized supercontinents at weak saddles, uses narrower coastal water bands, and keeps ruggedness separate from continent silhouette generation so the world does not collapse into directional stripes. Polar treatment, fog of war, map types, final tile art, gameplay systems, and final multi-player start placement are still intentionally deferred.
