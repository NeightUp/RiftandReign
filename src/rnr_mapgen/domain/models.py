"""Domain data models shared by generation and rendering."""

from __future__ import annotations

from dataclasses import dataclass, field

from rnr_mapgen.domain.hex import HexCoord


DEFAULT_WIDTH = 80
DEFAULT_HEIGHT = 40
DEFAULT_SEED = 0
DEFAULT_SEA_LEVEL = 0.39
DEFAULT_RIVER_SOURCE_THRESHOLD = 3.0
DEFAULT_PREVIEW_WIDTH = 32
DEFAULT_PREVIEW_HEIGHT = 16


@dataclass(frozen=True, slots=True)
class GeneratorConfig:
    """Deterministic world-generation configuration."""

    width: int = DEFAULT_WIDTH
    height: int = DEFAULT_HEIGHT
    seed: int = DEFAULT_SEED
    sea_level_threshold: float = DEFAULT_SEA_LEVEL
    river_source_threshold: float = DEFAULT_RIVER_SOURCE_THRESHOLD
    preview_width: int = DEFAULT_PREVIEW_WIDTH
    preview_height: int = DEFAULT_PREVIEW_HEIGHT

    def __post_init__(self) -> None:
        """Validate dimensions and user-facing generation controls."""
        if self.width <= 0:
            raise ValueError("width must be greater than zero")
        if self.height <= 0:
            raise ValueError("height must be greater than zero")
        if not 0.0 <= self.sea_level_threshold <= 1.0:
            raise ValueError("sea_level_threshold must be between 0.0 and 1.0")
        if self.river_source_threshold <= 0.0:
            raise ValueError("river_source_threshold must be greater than zero")
        if self.preview_width <= 0:
            raise ValueError("preview_width must be greater than zero")
        if self.preview_height <= 0:
            raise ValueError("preview_height must be greater than zero")


@dataclass(slots=True)
class TileData:
    """Map tile state for world generation and rendering."""

    coord: HexCoord
    display_col: int
    display_row: int
    elevation: float = 0.0
    continentality: float = 0.0
    ruggedness: float = 0.0
    is_water: bool = False
    water_class: str | None = None
    moisture: float = 0.0
    temperature: float = 0.0
    biome: str | None = None
    terrain_class: str | None = None
    river_flow_to: HexCoord | None = None
    flow_accumulation: float = 0.0
    has_river: bool = False
    river_strength: float = 0.0
    is_lake: bool = False
    start_suitability: float | None = None
    is_start_candidate: bool = False


@dataclass(slots=True)
class MapData:
    """Container for a generated world map."""

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
        """Return whether a coordinate exists in the playable field."""
        return coord in self.tiles


@dataclass(frozen=True, slots=True)
class ViewerConfig:
    """Configuration for the current map viewer."""

    enabled: bool = False
