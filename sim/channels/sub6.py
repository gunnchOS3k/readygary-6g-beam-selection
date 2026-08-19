"""3GPP-structure Sub-6 / FR1 channel draws.

Uses the existing ChannelBackend abstraction. Carrier frequency is a first-class
parameter (path loss, O2I, Doppler, carrier phase). Never copies FR2 28 GHz
SNR tables. SYNTHETIC_SIM. Not OTA, not Sionna unless that backend is used.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from sim.channels.backend import ChannelDraw, dft_steering
from sim.channels.tdl_cdl import DS_NS, PROFILES

C_LIGHT = 299792458.0


def uma_nlos_pathloss_db(distance_m: float, fc_hz: float, h_ut_m: float = 1.5) -> float:
    """TR 38.901 Table 7.4.1-1 UMa-NLOS (0.5-100 GHz). Digital, not a site survey."""
    d = max(float(distance_m), 10.0)
    fc_ghz = float(fc_hz) / 1e9
    return 13.54 + 39.08 * np.log10(d) + 20.0 * np.log10(fc_ghz) - 0.6 * (h_ut_m - 1.5)


def umi_nlos_pathloss_db(distance_m: float, fc_hz: float, h_ut_m: float = 1.5) -> float:
    d = max(float(distance_m), 10.0)
    fc_ghz = float(fc_hz) / 1e9
    return 22.4 + 35.3 * np.log10(d) + 21.3 * np.log10(fc_ghz) - 0.3 * (h_ut_m - 1.5)


def o2i_penetration_db(fc_hz: float, model: str = "low") -> float:
    """TR 38.901 Table 7.4.3-1/2 O2I building penetration (digital)."""
    fc = float(fc_hz) / 1e9
    if model == "high":
        l_glass = 23.0 + 0.3 * fc
        glass_frac, conc_frac = 0.7, 0.3
    else:
        l_glass = 2.0 + 0.2 * fc
        glass_frac, conc_frac = 0.3, 0.7
    l_concrete = 5.0 + 4.0 * fc
    mix = glass_frac * 10 ** (-l_glass / 10.0) + conc_frac * 10 ** (-l_concrete / 10.0)
    return float(5.0 - 10.0 * np.log10(max(mix, 1e-18)))


def doppler_hz(velocity_mps: float, fc_hz: float) -> float:
    return float(velocity_mps) * float(fc_hz) / C_LIGHT


def shadowing_db(rng: np.random.Generator, sigma_db: float) -> float:
    return float(rng.normal(0.0, sigma_db))


def _scenario_params(family: str, proto: dict[str, Any]) -> dict[str, Any]:
    ch = proto.get("channel") or {}
    indoor = family in {"indoor", "high_blockage"} or bool(ch.get("indoor"))
    congestion = family in {"congestion", "load_spike"}
    cell_edge = family in {"cell_edge"}
    distance = float(ch.get("distance_m", 80.0 if cell_edge else 35.0))
    if cell_edge:
        distance = float(ch.get("cell_edge_distance_m", 180.0))
    velocity = float(ch.get("velocity_mps", 1.5))
    if family in {"high_mobility", "mobility"}:
        velocity = float(ch.get("high_velocity_mps", 22.0))
    scenario = str(ch.get("scenario", "uma" if not indoor else "inh"))
    return {
        "indoor": indoor,
        "congestion": congestion,
        "cell_edge": cell_edge,
        "distance_m": distance,
        "velocity_mps": velocity,
        "scenario": scenario,
        "blockers": int(ch.get("blockers", 3 if indoor else 1)),
        "load": float(ch.get("load", 0.8 if congestion else 0.3)),
        "interference_db": float(ch.get("interference_db", 8.0 if congestion else 1.5)),
        "o2i_model": "high" if indoor else "low",
        "sigma_sf_db": 8.03 if indoor else 6.0,
    }


def superposition_at_fc(
    rng: np.random.Generator,
    delays_ns: list[float],
    powers_db: list[float],
    n_tx: int,
    n_rx: int,
    aoa0: float,
    aod0: float,
    mobility: float,
    fc_hz: float,
) -> tuple[np.ndarray, float, float]:
    """Delay/power profile → ULA H at fc. Sub-6 and FR2 must pass different fc."""
    H = np.zeros((n_tx, n_rx), dtype=np.complex128)
    for delay_ns, pdb in zip(delays_ns, powers_db):
        aoa = aoa0 + mobility * float(rng.normal(0.0, 0.08))
        aod = aod0 + mobility * float(rng.normal(0.0, 0.08))
        lin = 10.0 ** (pdb / 10.0)
        phase = 2 * np.pi * float(fc_hz) * (delay_ns * 1e-9) + float(rng.uniform(0, 2 * np.pi))
        H += np.sqrt(lin) * np.exp(1j * phase) * np.outer(dft_steering(n_tx, aod), dft_steering(n_rx, aoa))
    return H, aoa0, aod0


class Sub6ChannelBackend:
    """Open numpy Sub-6 backend. Parameterizes fc/path-loss/Doppler/O2I/load."""

    evidence_class = "SYNTHETIC_SIM"

    def __init__(self, profile: str = "tdl_a"):
        self.profile = profile
        self.name = f"sub6_{profile}"

    def available(self) -> tuple[bool, str]:
        return True, "open numpy Sub-6 TDL/UMa-NLOS; not OTA; not a 28 GHz relabel"

    def draw(self, rng: np.random.Generator, proto: dict[str, Any], family: str) -> ChannelDraw:
        carrier = proto.get("carrier") or {}
        fc = int(carrier.get("frequency_hz") or 3_750_000_000)
        if fc >= 6_000_000_000:
            raise ValueError(f"Sub-6 backend refused fc={fc}; not below 6 GHz")
        if abs(fc - 28_000_000_000) < 1_000_000:
            raise ValueError("Sub-6 backend refused 28 GHz")
        ch = proto.get("channel") or {}
        n_tx = int(ch.get("num_tx_ant", 4))
        n_rx = int(ch.get("num_rx_ant", 4))
        env = _scenario_params(family, proto)
        spec = PROFILES.get(self.profile, PROFILES["tdl_a"])
        ds = float(ch.get("delay_spread_ns", 363.0 if env["scenario"] == "uma" else 65.0))
        delays = [d * ds for d in spec["delays_norm"]]
        pl = uma_nlos_pathloss_db(env["distance_m"], fc) if env["scenario"] != "umi" else umi_nlos_pathloss_db(env["distance_m"], fc)
        if env["indoor"]:
            pl = pl + o2i_penetration_db(fc, env["o2i_model"]) + 0.5 * 8.0
        sf = shadowing_db(rng, env["sigma_sf_db"])
        fd = doppler_hz(env["velocity_mps"], fc)
        atten_db = pl + sf + env["interference_db"] * env["load"] + 1.5 * env["blockers"]
        # Convert large path loss into a relative tap scale vs a 0 dB reference.
        rel = -0.15 * (atten_db - 90.0)
        powers = [p + rel for p in spec["power_db"]]
        if family == "high_blockage":
            powers = [p - 8.0 for p in powers]
        mobility = max(0.25, env["velocity_mps"] / 8.0)
        aoa0 = float(rng.uniform(0.0, np.pi))
        aod0 = float(rng.uniform(0.0, np.pi))
        H, aoa, aod = superposition_at_fc(rng, delays, powers, n_tx, n_rx, aoa0, aod0, mobility, fc)
        return ChannelDraw(
            H=H,
            aoa=aoa,
            aod=aod,
            family=family,
            backend=self.name,
            evidence_class=self.evidence_class,
            provenance={
                "profile": self.profile.upper(),
                "source": "3GPP TR 38.901 TDL structure + UMa/UMi-NLOS + O2I (digital)",
                "carrier_hz": fc,
                "band": carrier.get("band", "FR1"),
                "family": carrier.get("family", "SUB6"),
                "band_id": carrier.get("band_id"),
                "below_6ghz": True,
                "path_loss_db": float(pl),
                "shadowing_db": float(sf),
                "o2i_db": float(o2i_penetration_db(fc, env["o2i_model"]) if env["indoor"] else 0.0),
                "doppler_hz": float(fd),
                "distance_m": env["distance_m"],
                "velocity_mps": env["velocity_mps"],
                "indoor": env["indoor"],
                "load": env["load"],
                "interference_db": env["interference_db"],
                "blockers": env["blockers"],
                "delay_spread_ns": ds,
                "n_tx": n_tx,
                "n_rx": n_rx,
                "calibrated_tr38901_geometry": False,
                "ota": False,
                "not": "FR2 28 GHz relabel",
            },
        )


def register_sub6_backends() -> dict[str, Sub6ChannelBackend]:
    return {
        "sub6_tdl_a": Sub6ChannelBackend("tdl_a"),
        "sub6_tdl_c": Sub6ChannelBackend("tdl_c"),
        "sub6_cdl_a": Sub6ChannelBackend("cdl_a"),
    }
