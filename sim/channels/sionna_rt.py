"""Optional NVIDIA Sionna RT backend. Open path must not import this as a hard dep."""
from __future__ import annotations

from typing import Any

import numpy as np

from sim.channels.backend import ChannelDraw
from sim.channels.synthetic import SyntheticBackend


class SionnaRtBackend:
    name = "sionna_rt"
    evidence_class = "SYNTHETIC_SIM"

    def available(self) -> tuple[bool, str]:
        try:
            import sionna  # noqa: F401
        except Exception as exc:
            return False, f"BLOCKED_OPTIONAL_BACKEND: sionna not importable ({type(exc).__name__})"
        return True, "sionna imported; still SYNTHETIC_SIM until scene+geometry are measured"

    def draw(self, rng: np.random.Generator, proto: dict[str, Any], family: str) -> ChannelDraw:
        ok, reason = self.available()
        if not ok:
            fallback = SyntheticBackend().draw(rng, proto, family)
            fallback.backend = self.name
            fallback.provenance = {
                **fallback.provenance,
                "sionna": reason,
                "used_fallback": "synthetic",
            }
            return fallback
        # Sionna is present: still do not invent an RT scene. Fall back with an honest flag.
        draw = SyntheticBackend().draw(rng, proto, family)
        draw.backend = self.name
        draw.provenance = {
            **draw.provenance,
            "sionna": "imported",
            "rt_scene": False,
            "note": "No committed NVIDIA scene; numpy fallback until OWNER_ACTION supplies AODT/Sionna scene.",
        }
        return draw
