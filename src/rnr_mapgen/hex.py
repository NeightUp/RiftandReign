"""Hex-grid coordinate utilities for pointy-top axial storage."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class CubeCoord:
    """Cube-coordinate helper representation for hex-grid algorithms."""

    x: int
    y: int
    z: int


@dataclass(frozen=True, slots=True)
class HexCoord:
    """Axial coordinate for a pointy-top hex grid."""

    q: int
    r: int

    _NEIGHBOR_OFFSETS: ClassVar[tuple[tuple[int, int], ...]] = (
        (1, 0),
        (1, -1),
        (0, -1),
        (-1, 0),
        (-1, 1),
        (0, 1),
    )

    def to_cube(self) -> CubeCoord:
        """Convert the axial coordinate to cube form."""
        x = self.q
        z = self.r
        y = -x - z
        return CubeCoord(x=x, y=y, z=z)

    def neighbor(self, direction: int) -> "HexCoord":
        """Return the neighboring axial coordinate for a direction index 0-5."""
        if direction < 0 or direction >= len(self._NEIGHBOR_OFFSETS):
            raise ValueError("direction must be in the range 0..5")
        dq, dr = self._NEIGHBOR_OFFSETS[direction]
        return HexCoord(self.q + dq, self.r + dr)

    def list_neighbors(self) -> list["HexCoord"]:
        """Return all six neighboring axial coordinates."""
        return [self.neighbor(direction) for direction in range(6)]

    def distance_to(self, other: "HexCoord") -> int:
        """Return the hex distance between two axial coordinates."""
        return cube_distance(self.to_cube(), other.to_cube())


def cube_distance(a: CubeCoord, b: CubeCoord) -> int:
    """Compute hex distance between two cube coordinates."""
    return max(abs(a.x - b.x), abs(a.y - b.y), abs(a.z - b.z))
