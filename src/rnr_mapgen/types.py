"""Core typed data structures for the RiftandReign map generator."""

from __future__ import annotations

from dataclasses import dataclass, field

from rnr_mapgen.hex import HexCoord


@dataclass(frozen=True, slots=True)
class GeneratorConfig:
    """Minimal deterministic configuration for map generation."""

    width: int
    height: int
    seed: int

    def __post_init__(self) -> None:
        """Validate dimensions for the finite playable field."""
        if self.width <= 0:
            raise ValueError("width must be greater than zero")
        if self.height <= 0:
            raise ValueError("height must be greater than zero")


@dataclass(slots=True)
class TileData:
    """Tile-level map data placeholder for future generation stages."""

    coord: HexCoord
    elevation: float = 0.0
    is_water: bool = False
    moisture: float = 0.0
    temperature: float = 0.0
    biome: str | None = None
    river_flow_to: HexCoord | None = None
    flow_accumulation: float = 0.0
    has_river: bool = False
    river_strength: float = 0.0
    is_lake: bool = False
    start_suitability: float | None = None
    is_start_candidate: bool = False


@dataclass(slots=True)
class MapData:
    """Container for generated tile data and generation metadata."""

    width: int
    height: int
    seed: int
    config: GeneratorConfig
    tiles: dict[HexCoord, TileData] = field(default_factory=dict)

    @property
    def tile_count(self) -> int:
        """Return the total number of tiles in the map."""
        return len(self.tiles)

    def contains(self, coord: HexCoord) -> bool:
        """Return whether the coordinate is within the playable field."""
        return coord in self.tiles
