"""Pluggable FR2 channel backends. Twin/sim ≠ OTA."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import numpy as np


@dataclass
class ChannelDraw:
    H: np.ndarray
    aoa: float
    aod: float
    family: str
    backend: str
    evidence_class: str
    provenance: dict[str, Any] = field(default_factory=dict)


class ChannelBackend(Protocol):
    name: str
    evidence_class: str

    def available(self) -> tuple[bool, str]:
        ...

    def draw(self, rng: np.random.Generator, proto: dict[str, Any], family: str) -> ChannelDraw:
        ...


def dft_steering(n_ant: int, angle: float) -> np.ndarray:
    return np.exp(1j * np.pi * np.arange(n_ant) * np.cos(angle)) / np.sqrt(n_ant)
