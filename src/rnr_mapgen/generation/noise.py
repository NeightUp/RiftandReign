"""Deterministic low-frequency noise helpers for map generation."""

from __future__ import annotations

import math
from hashlib import blake2b


def axis_ratio(index: int, size: int) -> float:
    """Convert a board index into a stable 0.0..1.0 ratio."""
    if size <= 1:
        return 0.5
    return index / (size - 1)


def clamp_unit(value: float) -> float:
    """Clamp a scalar value into the 0.0..1.0 range."""
    return max(0.0, min(1.0, value))


def hash_unit_interval(seed: int, label: str, x: int, y: int) -> float:
    """Return a deterministic pseudo-random value in the range 0.0..1.0."""
    payload = f"{seed}:{label}:{x}:{y}".encode("ascii")
    digest = blake2b(payload, digest_size=8).digest()
    numerator = int.from_bytes(digest, byteorder="big")
    return numerator / ((1 << 64) - 1)


def value_noise(seed: int, label: str, x_ratio: float, y_ratio: float, scale: float) -> float:
    """Return smooth deterministic 2D value noise in the 0.0..1.0 range."""
    x = x_ratio * scale
    y = y_ratio * scale
    x0 = math.floor(x)
    y0 = math.floor(y)
    x1 = x0 + 1
    y1 = y0 + 1
    tx = x - x0
    ty = y - y0

    v00 = hash_unit_interval(seed, label, x0, y0)
    v10 = hash_unit_interval(seed, label, x1, y0)
    v01 = hash_unit_interval(seed, label, x0, y1)
    v11 = hash_unit_interval(seed, label, x1, y1)

    sx = smoothstep(tx)
    sy = smoothstep(ty)
    i0 = lerp(v00, v10, sx)
    i1 = lerp(v01, v11, sx)
    return lerp(i0, i1, sy)


def wrapped_value_noise(seed: int, label: str, x_ratio: float, y_ratio: float, scale: float) -> float:
    """Return smooth deterministic value noise that wraps horizontally."""
    x = x_ratio * scale
    y = y_ratio * scale
    period = max(1, int(math.ceil(scale)))
    x0 = math.floor(x) % period
    y0 = math.floor(y)
    x1 = (x0 + 1) % period
    y1 = y0 + 1
    tx = x - math.floor(x)
    ty = y - y0

    v00 = hash_unit_interval(seed, label, x0, y0)
    v10 = hash_unit_interval(seed, label, x1, y0)
    v01 = hash_unit_interval(seed, label, x0, y1)
    v11 = hash_unit_interval(seed, label, x1, y1)

    sx = smoothstep(tx)
    sy = smoothstep(ty)
    i0 = lerp(v00, v10, sx)
    i1 = lerp(v01, v11, sx)
    return lerp(i0, i1, sy)


def wrapped_fbm_noise(
    seed: int,
    label: str,
    x_ratio: float,
    y_ratio: float,
    base_scale: float,
    octaves: int = 4,
    lacunarity: float = 2.0,
    persistence: float = 0.5,
) -> float:
    """Return horizontally wrapped fractal value noise in the 0.0..1.0 range."""
    amplitude = 1.0
    frequency = 1.0
    total = 0.0
    weight_sum = 0.0

    for octave in range(octaves):
        total += amplitude * wrapped_value_noise(
            seed + octave,
            f"{label}_{octave}",
            x_ratio,
            y_ratio,
            base_scale * frequency,
        )
        weight_sum += amplitude
        amplitude *= persistence
        frequency *= lacunarity

    if weight_sum == 0.0:
        return 0.5
    return total / weight_sum


def smoothstep(value: float) -> float:
    """Return a smooth interpolation factor in the 0.0..1.0 range."""
    return value * value * (3.0 - (2.0 * value))


def lerp(start: float, end: float, factor: float) -> float:
    """Linearly interpolate between two values."""
    return start + ((end - start) * factor)
