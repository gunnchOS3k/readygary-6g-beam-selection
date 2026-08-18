"""Seeded synthetic ULA draws (existing Paper II generator). SYNTHETIC_SIM. Not OTA."""
from __future__ import annotations

from typing import Any

import numpy as np

from sim.channels.backend import ChannelDraw, dft_steering
from sim.experiments.digital_programme import generate_slot


class SyntheticBackend:
    name = "synthetic"
    evidence_class = "SYNTHETIC_SIM"

    def available(self) -> tuple[bool, str]:
        return True, "open numpy path"

    def draw(self, rng: np.random.Generator, proto: dict[str, Any], family: str) -> ChannelDraw:
        slot = generate_slot(rng, proto, family)
        return ChannelDraw(
            H=slot.H,
            aoa=slot.aoa,
            aod=slot.aod,
            family=family,
            backend=self.name,
            evidence_class=self.evidence_class,
            provenance={
                "generator": "seeded_synthetic_tdl_ula",
                "carrier_hz": 28_000_000_000,
                "band": "FR2",
                "not": "OTA / TR 38.901 campaign",
            },
        )


def superposition_from_paths(
    rng: np.random.Generator,
    delays_ns: list[float],
    powers_db: list[float],
    n_tx: int,
    n_rx: int,
    aoa0: float,
    aod0: float,
    mobility: float,
) -> tuple[np.ndarray, float, float]:
    """Delay/power profile → ULA H. Frequency 28 GHz is a label, not a measured RF chain."""
    H = np.zeros((n_tx, n_rx), dtype=np.complex128)
    for delay_ns, pdb in zip(delays_ns, powers_db):
        aoa = aoa0 + mobility * float(rng.normal(0.0, 0.08))
        aod = aod0 + mobility * float(rng.normal(0.0, 0.08))
        lin = 10.0 ** (pdb / 10.0)
        phase = 2 * np.pi * 28e9 * (delay_ns * 1e-9) + float(rng.uniform(0, 2 * np.pi))
        H += np.sqrt(lin) * np.exp(1j * phase) * np.outer(dft_steering(n_tx, aod), dft_steering(n_rx, aoa))
    return H, aoa0, aod0
