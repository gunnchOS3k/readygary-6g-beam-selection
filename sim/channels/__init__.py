"""Pluggable FR2 channel backends. Open numpy path does not require NVIDIA software."""
from __future__ import annotations

from sim.channels.aodt import AodtBackend
from sim.channels.backend import ChannelDraw
from sim.channels.sionna_rt import SionnaRtBackend
from sim.channels.synthetic import SyntheticBackend
from sim.channels.tdl_cdl import TdlCdlBackend

BACKENDS = {
    "synthetic": SyntheticBackend(),
    "tdl_a": TdlCdlBackend("tdl_a"),
    "tdl_c": TdlCdlBackend("tdl_c"),
    "cdl_a": TdlCdlBackend("cdl_a"),
    "sionna_rt": SionnaRtBackend(),
    "aodt": AodtBackend(),
}


def get_backend(name: str):
    if name not in BACKENDS:
        raise KeyError(f"Unknown channel backend {name}")
    return BACKENDS[name]


def availability_report() -> dict[str, dict[str, str | bool]]:
    out: dict[str, dict[str, str | bool]] = {}
    for name, be in BACKENDS.items():
        ok, reason = be.available()
        out[name] = {
            "available": ok,
            "reason": reason,
            "evidence_class": be.evidence_class,
        }
    return out


__all__ = ["BACKENDS", "ChannelDraw", "availability_report", "get_backend"]
