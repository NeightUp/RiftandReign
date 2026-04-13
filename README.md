# RiftandReign Map Generator

This repository contains the foundation for a deterministic map generator for a hex-based 4X strategy game. The current step establishes the package layout, project documentation, project-tracking files, tested hex-grid utilities, a deterministic finite board/data layer, scalar fields, first-pass land and water classification, first-pass hydrology groundwork, first-pass biome classification, first-pass start suitability scoring, and configurable CLI-driven map generation.

The repository is focused on the map generator only. The intended long-term pipeline is:

1. seed and configuration
2. scalar field generation
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
- finite non-wrapping board construction
- deterministic scalar fields for elevation, moisture, and temperature
- deterministic first-pass land and water classification
- deterministic first-pass hydrology and river marking
- deterministic first-pass biome classification
- deterministic first-pass start suitability scoring
- configurable CLI-driven map generation for larger maps and seed testing
- debug-oriented CLI terrain, river, biome, and start summary with ASCII preview
- documentation for scope, map spec, pipeline, and data model
- project tracking via changelog and detailed change notes
- focused tests

Out of scope right now:

- actual map generation
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
python -m rnr_mapgen --width 24 --height 16 --seed 5
rnr-mapgen --width 40 --height 24 --seed 123 --preview-width 24 --preview-height 12
```

## Documentation

Start with [docs/repo_index.md](docs/repo_index.md). It is the authoritative navigation file for the repository and points to the scope, spec, pipeline, data model, workflow, tests, and change history.

## Current Status

The CLI now accepts explicit map configuration for width, height, seed, sea level, river source threshold, and ASCII preview size. Larger maps use a deterministic top-left preview crop so terminal output remains readable. Final multi-player start placement and start validation are still intentionally deferred.
