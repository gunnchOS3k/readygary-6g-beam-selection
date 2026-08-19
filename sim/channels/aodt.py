"""Optional Aerial Omniverse Digital Twin adapter. No NVIDIA credentials in-tree.

Fail closed. Field-kit convention: UNAVAILABLE_FAIL_CLOSED, silent fake forbidden.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from sim.channels.backend import ChannelDraw
from sim.channels.synthetic import SyntheticBackend


class AodtBackend:
    name = "aodt"
    evidence_class = "SYNTHETIC_SIM"

    def available(self) -> tuple[bool, str]:
        for mod in ("aodt", "aerial", "pyaerial"):
            try:
                __import__(mod)
                return True, f"{mod} importable; scene access still required (BLOCKED_MEMBER_ACCESS until scene)"
            except Exception:
                continue
        return False, "BLOCKED_EXTERNAL: AODT/Aerial/pyAerial not importable"

    def draw(self, rng: np.random.Generator, proto: dict[str, Any], family: str) -> ChannelDraw:
        ok, reason = self.available()
        carrier = proto.get("carrier") or {}
        fc = float(carrier.get("frequency_hz", 28e9))
        if fc < 6e9 and str(carrier.get("family", "")) == "SUB6":
            from sim.channels.sub6 import Sub6ChannelBackend

            draw = Sub6ChannelBackend().draw(rng, proto, family)
            fallback_name = "sub6_tdl"
        else:
            draw = SyntheticBackend().draw(rng, proto, family)
            fallback_name = "synthetic"
        draw.backend = self.name
        draw.provenance = {
            **draw.provenance,
            "aodt": reason,
            "status": "BLOCKED_EXTERNAL" if not ok else "IMPLEMENTED_NOT_EXECUTED",
            "used_fallback": fallback_name,
            "silent_fake_forbidden": True,
            "ota": False,
            "credentials_committed": False,
        }
        return draw
