"""Parametric 3GPP TDL/CDL *structure* at 28 GHz FR2.

Evidence: SYNTHETIC_SIM. This is not a calibrated TR 38.901 geometry, not OTA,
and not a claim that Sionna/Quadriga was used.
Delay/power taps follow the public 3GPP TR 38.901 TDL-A / TDL-C / CDL-A tables
(normalized delays × 300 ns DS for indoor-ish scale) as a digital stand-in.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from sim.channels.backend import ChannelDraw
from sim.channels.synthetic import superposition_from_paths

# Public TR 38.901 Table 7.7.2-1 (TDL-A) and 7.7.2-3 (TDL-C): normalized delay, power dB.
# Scaled by ds_ns so the profile is a structure, not a site measurement.
TDL_A = {
    "delays_norm": [0.0, 0.3819, 0.4025, 0.5868, 0.4610, 0.5375, 0.6708, 0.5750, 0.7618, 1.5375, 1.8978, 2.2242, 2.1718, 2.4942, 2.5119, 3.0582, 4.0810, 4.4577, 4.5695, 4.7966, 5.0066, 5.3043, 9.6586],
    "power_db": [-13.4, 0.0, -2.2, -4.0, -6.0, -8.2, -9.9, -10.5, -7.5, -15.9, -6.6, -16.7, -12.4, -15.2, -10.8, -11.3, -12.7, -16.2, -18.3, -18.9, -16.6, -19.9, -29.7],
}
TDL_C = {
    "delays_norm": [0.0, 0.2099, 0.2219, 0.2329, 0.2176, 0.6366, 0.6448, 0.6560, 0.6584, 0.7935, 0.8213, 0.9336, 1.2285, 1.3083, 2.1704, 2.7105, 4.2589, 4.6008, 5.4902, 5.6077, 6.3062, 6.6374, 7.0427, 8.6523],
    "power_db": [-4.4, -1.2, -3.5, -5.2, -2.5, 0.0, -2.2, -3.9, -7.4, -7.1, -10.7, -11.1, -5.1, -6.8, -8.7, -13.2, -13.9, -13.9, -15.8, -17.1, -16.0, -15.7, -21.6, -22.8],
}
# CDL-A cluster delays (Table 7.7.1-1) — first 13 clusters, powers dB.
CDL_A = {
    "delays_norm": [0.0, 0.0489, 0.0574, 0.1322, 0.2415, 0.2626, 0.7011, 0.8899, 0.9335, 1.2285, 1.3083, 2.1704, 2.7105],
    "power_db": [-13.4, 0.0, -2.2, -4.0, -6.0, -8.2, -9.9, -10.5, -7.5, -15.9, -6.6, -16.7, -12.4],
}

PROFILES = {"tdl_a": TDL_A, "tdl_c": TDL_C, "cdl_a": CDL_A}
DS_NS = 300.0  # digital scale, not a measured delay spread


class TdlCdlBackend:
    evidence_class = "SYNTHETIC_SIM"

    def __init__(self, profile: str):
        if profile not in PROFILES:
            raise ValueError(profile)
        self.profile = profile
        self.name = profile

    def available(self) -> tuple[bool, str]:
        return True, "parametric 3GPP TDL/CDL structure; open numpy; not OTA"

    def draw(self, rng: np.random.Generator, proto: dict[str, Any], family: str) -> ChannelDraw:
        ch = proto.get("channel") or {}
        n_tx = int(ch.get("num_tx_ant", 8))
        n_rx = int(ch.get("num_rx_ant", 8))
        mobility = 4.0 if family == "high_mobility" else 1.0
        atten = 0.35 if family == "high_blockage" else 1.0
        spec = PROFILES[self.profile]
        delays = [d * DS_NS for d in spec["delays_norm"]]
        powers = [p + (10.0 * np.log10(atten) if atten < 1 else 0.0) for p in spec["power_db"]]
        aoa0 = float(rng.uniform(0.0, np.pi))
        aod0 = float(rng.uniform(0.0, np.pi))
        H, aoa, aod = superposition_from_paths(rng, delays, powers, n_tx, n_rx, aoa0, aod0, mobility)
        return ChannelDraw(
            H=H,
            aoa=aoa,
            aod=aod,
            family=family,
            backend=self.name,
            evidence_class=self.evidence_class,
            provenance={
                "profile": self.profile.upper(),
                "source": "3GPP TR 38.901 table structure (public)",
                "delay_spread_ns_digital_scale": DS_NS,
                "carrier_hz": 28_000_000_000,
                "band": "FR2",
                "calibrated_tr38901_geometry": False,
                "ota": False,
            },
        )
