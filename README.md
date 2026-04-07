# RiftandReign Map Generator

This repository contains the foundation for a deterministic map generator for a hex-based 4X strategy game. The current step establishes the package layout, project documentation, project-tracking files, tested hex-grid utilities, and a deterministic finite board/data layer needed before terrain generation work begins.

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
- debug-oriented CLI board summary
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

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .[dev]
```

Run the board foundation entry point:

```bash
python -m rnr_mapgen
```

Or:

```bash
rnr-mapgen
```

Run tests:

```bash
pytest
```

## Documentation

Start with [docs/repo_index.md](docs/repo_index.md). It is the authoritative navigation file for the repository and points to the scope, spec, pipeline, data model, tests, and change history.

## Current Status

The CLI now builds an empty deterministic board from a default config and prints a concise summary of the board dimensions, seed, tile count, and a small coordinate sample. Terrain generation, hydrology, climate, biome assignment, and validation logic are still intentionally deferred.
