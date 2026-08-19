"""Optional NVIDIA Sionna RT backend. Open path must not import this as a hard dep.

Classification:
- sionna missing → BLOCKED_EXTERNAL / IMPLEMENTED_NOT_EXECUTED
- sionna present but no scene → IMPLEMENTED_NOT_EXECUTED (honest numpy fallback)
- sionna RT scene executed → IMPLEMENTED_AND_EXECUTED (owner/lab only)
"""
from __future__ import annotations

from typing import Any

import numpy as np

from sim.channels.backend import ChannelDraw
from sim.channels.synthetic import SyntheticBackend


def _try_sionna_tdl(rng: np.random.Generator, proto: dict[str, Any], family: str) -> tuple[np.ndarray | None, dict[str, Any]]:
    """Attempt Sionna PHY TDL at the protocol carrier. Never invent a scene."""
    meta: dict[str, Any] = {"sionna_phy": False, "sionna_rt": False}
    try:
        import sionna  # noqa: F401
    except Exception as exc:
        meta["status"] = "BLOCKED_EXTERNAL"
        meta["reason"] = f"sionna not importable ({type(exc).__name__})"
        return None, meta
    fc = float((proto.get("carrier") or {}).get("frequency_hz", 28e9))
    n_tx = int((proto.get("channel") or {}).get("num_tx_ant", 8))
    n_rx = int((proto.get("channel") or {}).get("num_rx_ant", 8))
    # Newer sionna.phy.channel.tr38901.TDL or older sionna.channel.tr38901.TDL
    tdl_cls = None
    try:
        from sionna.phy.channel.tr38901 import TDL as tdl_cls  # type: ignore
    except Exception:
        try:
            from sionna.channel.tr38901 import TDL as tdl_cls  # type: ignore
        except Exception as exc:
            meta["status"] = "IMPLEMENTED_NOT_EXECUTED"
            meta["reason"] = f"sionna imported but TDL class missing ({type(exc).__name__})"
            return None, meta
    try:
        model = tdl_cls("A", delay_spread=300e-9, carrier_frequency=fc)
        # API varies by Sionna version; fail closed to numpy rather than fabricate.
        if hasattr(model, "__call__"):
            h = model(batch_size=1, num_time_steps=1)
            arr = np.array(h)
            meta["sionna_phy"] = True
            meta["status"] = "IMPLEMENTED_AND_EXECUTED"
            meta["note"] = "Sionna TDL call succeeded; still SYNTHETIC_SIM, not OTA"
            if arr.ndim >= 2:
                flat = arr.reshape(-1)
                # Collapse to n_tx x n_rx for the existing scorer.
                need = n_tx * n_rx
                if flat.size < need:
                    flat = np.pad(flat, (0, need - flat.size))
                H = flat[:need].reshape(n_tx, n_rx).astype(np.complex128)
                return H, meta
        meta["status"] = "IMPLEMENTED_NOT_EXECUTED"
        meta["reason"] = "Sionna TDL constructed but call/shape not usable"
        return None, meta
    except Exception as exc:
        meta["status"] = "IMPLEMENTED_NOT_EXECUTED"
        meta["reason"] = f"Sionna TDL execution failed ({type(exc).__name__})"
        return None, meta


class SionnaRtBackend:
    name = "sionna_rt"
    evidence_class = "SYNTHETIC_SIM"

    def available(self) -> tuple[bool, str]:
        try:
            import sionna  # noqa: F401
        except Exception as exc:
            return False, f"BLOCKED_EXTERNAL: sionna not importable ({type(exc).__name__})"
        return True, "sionna imported; RT scene still required for IMPLEMENTED_AND_EXECUTED RT"

    def draw(self, rng: np.random.Generator, proto: dict[str, Any], family: str) -> ChannelDraw:
        ok, _ = self.available()
        H, meta = _try_sionna_tdl(rng, proto, family)
        if H is not None:
            return ChannelDraw(
                H=H,
                aoa=0.0,
                aod=0.0,
                family=family,
                backend=self.name,
                evidence_class=self.evidence_class,
                provenance={**meta, "rt_scene": False, "ota": False},
            )
        carrier = proto.get("carrier") or {}
        fc = float(carrier.get("frequency_hz", 28e9))
        if fc < 6e9 and str(carrier.get("family", "")) == "SUB6":
            from sim.channels.sub6 import Sub6ChannelBackend

            fallback = Sub6ChannelBackend().draw(rng, proto, family)
        else:
            fallback = SyntheticBackend().draw(rng, proto, family)
        fallback.backend = self.name
        fallback.provenance = {
            **fallback.provenance,
            **meta,
            "used_fallback": "sub6_tdl" if fc < 6e9 else "synthetic",
            "rt_scene": False,
            "ota": False,
            "sionna_available": ok,
        }
        return fallback
