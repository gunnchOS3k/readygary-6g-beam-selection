"""Sub-6 digital programme. SYNTHETIC_SIM. Distinct from FR2 28 GHz."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from sim.access import rank_csi, select_cell, type1_codebook
from sim.bands import experiment_carrier, load_all_profiles, primary_sub6
from sim.channels import get_backend
from sim.channels.sub6 import doppler_hz, uma_nlos_pathloss_db
from sim.experiments.digital_programme import dft_codebook, exhaustive, mean_ci

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "paper" / "artifacts" / "experiment_protocol_sub6.yaml"


def load_sub6_protocol(path: Path = PROTOCOL) -> dict[str, Any]:
    from sim.experiments.digital_programme import _mini_yaml_load

    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
    except Exception:
        data = _mini_yaml_load(text)
    if not isinstance(data, dict) or data.get("frozen") is not True:
        raise ValueError("Sub-6 protocol must be frozen")
    carrier = data.get("carrier") or {}
    fc = int(carrier.get("frequency_hz") or 0)
    if fc >= 6_000_000_000:
        raise ValueError("Sub-6 protocol fc must be below 6 GHz")
    if str(carrier.get("family")) != "SUB6":
        raise ValueError("Sub-6 protocol family must be SUB6")
    if abs(fc - 28_000_000_000) < 1_000_000:
        raise ValueError("28 GHz is not Sub-6")
    return data


def _proto_for_profile(base: dict[str, Any], profile_id: str) -> dict[str, Any]:
    prof = load_all_profiles()[profile_id]
    out = json.loads(json.dumps(base))
    out["carrier"] = experiment_carrier(prof)
    ch = dict(out.get("channel") or {})
    n_ant = 2 if prof.band_id == "n71" else 4
    ch["num_tx_ant"] = n_ant
    ch["num_rx_ant"] = n_ant
    out["channel"] = ch
    return out


def _slot_metrics(draw, proto: dict[str, Any]) -> dict[str, float]:
    H = draw.H
    n = H.shape[0]
    cb = type1_codebook(n, min(8, n * 2))
    csi = rank_csi(H, cb)
    tx = dft_codebook(n, n)
    _, _, snr_ex = exhaustive(H, tx, tx)
    return {
        "csi_score": float(csi["csi_score"]),
        "snr_exhaustive_linear": float(snr_ex),
        "snr_exhaustive_db": float(10.0 * math.log10(max(snr_ex, 1e-18))),
        "path_loss_db": float(draw.provenance.get("path_loss_db", math.nan)),
        "doppler_hz": float(draw.provenance.get("doppler_hz", math.nan)),
        "carrier_hz": float(draw.provenance.get("carrier_hz", 0.0)),
    }


def run_family(proto: dict[str, Any], family: str, seeds: list[int]) -> dict[str, Any]:
    backend = get_backend(str((proto.get("channel") or {}).get("backend", "sub6_tdl_a")))
    n_ep = int((proto.get("split") or {}).get("n_episodes_per_seed", 8))
    n_sl = int((proto.get("split") or {}).get("n_slots_per_episode", 6))
    seed_means: dict[str, list[float]] = {
        "snr_exhaustive_db": [],
        "path_loss_db": [],
        "doppler_hz": [],
        "csi_score": [],
    }
    for seed in seeds:
        rng = np.random.default_rng(int(seed))
        acc = {k: [] for k in seed_means}
        for _ in range(n_ep):
            for _s in range(n_sl):
                draw = backend.draw(rng, proto, family)
                m = _slot_metrics(draw, proto)
                for k in acc:
                    acc[k].append(m[k])
        for k in seed_means:
            seed_means[k].append(float(sum(acc[k]) / max(len(acc[k]), 1)))
    return {
        "family": family,
        "carrier_hz": int((proto.get("carrier") or {}).get("frequency_hz")),
        "band_id": (proto.get("carrier") or {}).get("band_id"),
        "below_6ghz": True,
        "evidence_class": "SYNTHETIC_SIM",
        "metrics": {k: mean_ci(v) for k, v in seed_means.items()},
        "seeds": seeds,
    }


def fspl_gap_db(fc_a: float, fc_b: float) -> float:
    return float(20.0 * math.log10(fc_b / fc_a))


def run_programme(*, heldout: bool = False) -> dict[str, Any]:
    proto = load_sub6_protocol()
    split = proto["split"]
    seeds = list(split["held_out_seeds"] if heldout else split["train_seeds"])
    families = [split["train_family"]]
    if heldout:
        families = [split["held_out_family"]] + list(split.get("domain_shift_families") or [])
    primary = primary_sub6()
    bundle: dict[str, Any] = {
        "experiment_id": proto["experiment_id"],
        "heldout": heldout,
        "evidence_class": "SYNTHETIC_SIM",
        "latency_class": "HOST_PROCESS_TIMING",
        "sub_ms_inference_proven": False,
        "primary_profile": primary.profile_id,
        "carrier": proto["carrier"],
        "families": {},
        "supporting": {},
        "fspl_gap_vs_28ghz_db": fspl_gap_db(primary.fc_hz, 28e9),
        "uma_pl_35m_n77_db": uma_nlos_pathloss_db(35.0, primary.fc_hz),
        "uma_pl_35m_n257_db": uma_nlos_pathloss_db(35.0, 28e9),
        "doppler_22mps_n77_hz": doppler_hz(22.0, primary.fc_hz),
        "doppler_22mps_n257_hz": doppler_hz(22.0, 28e9),
        "never": "28 GHz as Sub-6; FR2 relabel; OTA",
    }
    pproto = _proto_for_profile(proto, primary.profile_id)
    for fam in families:
        bundle["families"][fam] = run_family(pproto, fam, seeds)
    if heldout:
        for pid in proto.get("supporting_profiles") or []:
            sp = _proto_for_profile(proto, pid)
            bundle["supporting"][pid] = run_family(sp, "in_distribution", seeds[:2])
    # Distinctness gate vs FR2 frozen table if present.
    fr2_path = ROOT / "results" / "experiments" / "rq2_beam_selection_fr2_heldout.json"
    if fr2_path.is_file():
        fr2 = json.loads(fr2_path.read_text(encoding="utf-8"))
        bundle["fr2_heldout_carrier_hz"] = 28_000_000_000
        bundle["distinct_from_fr2_carrier"] = bundle["carrier"]["frequency_hz"] != 28_000_000_000
        bundle["fr2_experiment_id"] = fr2.get("experiment_id")
    return bundle


def write_bundle(bundle: dict[str, Any], heldout: bool) -> Path:
    out = ROOT / "results" / "experiments"
    out.mkdir(parents=True, exist_ok=True)
    name = "rq2_sub6_fr1_heldout.json" if heldout else "rq2_sub6_fr1_train.json"
    path = out / name
    path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    return path
