"""Compatibility exports for generation noise helpers."""

from rnr_mapgen.generation.noise import (
    axis_ratio,
    clamp_unit,
    hash_unit_interval,
    lerp,
    smoothstep,
    wrapped_fbm_noise,
    value_noise,
    wrapped_value_noise,
)

__all__ = [
    "axis_ratio",
    "clamp_unit",
    "hash_unit_interval",
    "lerp",
    "smoothstep",
    "wrapped_fbm_noise",
    "value_noise",
    "wrapped_value_noise",
]
