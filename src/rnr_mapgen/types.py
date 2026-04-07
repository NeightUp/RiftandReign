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
    is_lake: bool = False
    start_suitability: float | None = None


@dataclass(slots=True)
class MapData:
    """Container for generated tile data and generation metadata."""

    width: int
    height: int
    seed: int
    config: GeneratorConfig
    tiles: dict[HexCoord, TileData] = field(default_factory=dict)
