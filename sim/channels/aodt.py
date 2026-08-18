"""Optional Aerial Omniverse Digital Twin adapter. No NVIDIA credentials in-tree."""
from __future__ import annotations

from typing import Any

import numpy as np

from sim.channels.backend import ChannelDraw
from sim.channels.synthetic import SyntheticBackend


class AodtBackend:
    name = "aodt"
    evidence_class = "SYNTHETIC_SIM"

    def available(self) -> tuple[bool, str]:
        try:
            import aodt  # noqa: F401
        except Exception:
            try:
                import aerial  # noqa: F401
            except Exception as exc:
                return False, f"BLOCKED_OPTIONAL_BACKEND: AODT/Aerial not importable ({type(exc).__name__})"
        return True, "AODT/Aerial importable; scene access still required"

    def draw(self, rng: np.random.Generator, proto: dict[str, Any], family: str) -> ChannelDraw:
        ok, reason = self.available()
        draw = SyntheticBackend().draw(rng, proto, family)
        draw.backend = self.name
        draw.provenance = {
            **draw.provenance,
            "aodt": reason if not ok else "imported_no_scene",
            "used_fallback": "synthetic",
            "ota": False,
        }
        return draw
