# Acceptance Tests

These are project-level acceptance criteria for the eventual generator. They are broader than unit tests and describe what the completed generator must reliably satisfy.

## Determinism

- The same seed and configuration produce identical map outputs across repeated runs.
- Different seeds can produce different maps without breaking structural validity.

## Grid Math

- Hex neighbor calculations are correct for pointy-top axial coordinates.
- Distance calculations are symmetric and return zero for a tile compared with itself.

## Scalar Fields

- Every generated tile receives deterministic elevation, moisture, and temperature scalar values.
- Scalar values remain within the expected normalized range used by later pipeline stages.

## Land And Water Classification

- Every generated tile receives a land or water classification.
- The same seed and configuration produce the same terrain layout.
- Terrain output should contain coherent land and water patches rather than isolated salt-and-pepper noise.

## Hydrology

- No river path moves uphill.
- River features are only marked on land tiles.
- First-pass hydrology produces deterministic downhill routing and some river presence on supported maps.
- Full lake or ocean termination behavior remains a later milestone.

## Climate And Biomes

- Every generated tile receives a biome assignment.
- Water tiles remain distinct from land biome labels.
- The default supported map setup should produce multiple land biome types rather than a single uniform land class.
- Moisture and temperature data are present on every tile where required by the biome layer.

## Starting Regions

- Candidate starting regions must contain enough practical land to begin play.
- Candidate starting regions must avoid obviously invalid terrain traps such as isolated unusable tiles or impossible early expansion.
- Start validation must be deterministic for a fixed map and rule set.

## Runtime Stability

- The generator runs without crashes for supported configuration ranges.
- Debug-oriented outputs can be produced for inspection when validation fails.
