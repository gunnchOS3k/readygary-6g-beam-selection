"""Dual-band + failure experiments. Min-useful service primary. SYNTHETIC_SIM."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from sim.access.radio_decision import RadioDecisionContext
from sim.devices import continuity_context_defaults
from sim.dualband.controller import POLICIES, decide
from sim.experiments.digital_programme import dft_codebook, mean_ci
from sim.models.gnn_trainable import classify_existing_gnn, run_trainable, train_on_oracle
from sim.policies.sequential_band import classify_rl, train_sequential
from sim.policies.sequential_band import classify_rl, train_sequential

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "paper" / "artifacts" / "experiment_protocol_dualband.yaml"

FAILURES = (
    "nominal",
    "fr2_blockage",
    "sub6_congestion",
    "cell_edge",
    "mobility",
    "indoor",
    "backhaul",
    "compute_unavailability",
    "load_spike",
    "simultaneous",
    "recovery",
)


def load_dual_protocol(path: Path = PROTOCOL) -> dict[str, Any]:
    from sim.experiments.digital_programme import _mini_yaml_load

    text = path.read_text(encoding="utf-8")
    try:
        import yaml

        data = yaml.safe_load(text)
    except Exception:
        data = _mini_yaml_load(text)
    if not isinstance(data, dict) or data.get("frozen") is not True:
        raise ValueError("Dual-band protocol must be frozen")
    sub6 = (data.get("carriers") or {}).get("sub6") or {}
    fr2 = (data.get("carriers") or {}).get("fr2") or {}
    if int(sub6.get("frequency_hz") or 0) >= 6_000_000_000:
        raise ValueError("Dual-band Sub-6 carrier must be below 6 GHz")
    if int(fr2.get("frequency_hz") or 0) != 28_000_000_000:
        raise ValueError("Dual-band FR2 carrier must remain 28 GHz")
    if str(fr2.get("never")) != "Sub-6":
        raise ValueError("FR2 must declare never: Sub-6")
    return data


def _measurements(failure: str, rng: np.random.Generator) -> dict[str, Any]:
    m: dict[str, Any] = {
        "sinr_sub6_db": float(rng.normal(12.0, 2.0)),
        "sinr_fr2_db": float(rng.normal(14.0, 3.0)),
        "rate_sub6_mbps": 50.0,
        "rate_fr2_mbps": 900.0,
        "congestion": 0.2,
        "fr2_blockage": False,
        "indoor": False,
        "velocity_mps": 1.5,
        "rsrp_dbm": [-88.0, -94.0, -101.0],
        "compute_placement": "local",
        "backhaul_ok": True,
        "min_useful_mbps": 2.0,
        "preferred_family": "SUB6",
    }
    if failure == "fr2_blockage":
        m["fr2_blockage"] = True
        m["sinr_fr2_db"] = -8.0
        m["rate_fr2_mbps"] = 0.0
    elif failure == "sub6_congestion":
        m["congestion"] = 0.92
        m["rate_sub6_mbps"] = 1.2
        m["sinr_sub6_db"] = 3.0
    elif failure == "cell_edge":
        m["sinr_sub6_db"] = 1.5
        m["sinr_fr2_db"] = -2.0
        m["rate_sub6_mbps"] = 0.8
        m["rate_fr2_mbps"] = 1.2
        m["rsrp_dbm"] = [-108.0, -110.0, -112.0]
    elif failure == "mobility":
        m["velocity_mps"] = 25.0
        m["sinr_fr2_db"] = 4.0
    elif failure == "indoor":
        m["indoor"] = True
        m["fr2_blockage"] = True
        m["sinr_fr2_db"] = -12.0
        m["sinr_sub6_db"] = 7.0
    elif failure == "backhaul":
        m["backhaul_ok"] = False
        m["compute_placement"] = "local"
        m["rate_fr2_mbps"] = 0.0
    elif failure == "compute_unavailability":
        m["compute_placement"] = "unavailable"
    elif failure == "load_spike":
        m["congestion"] = 0.85
        m["load"] = 0.95
    elif failure == "simultaneous":
        m["fr2_blockage"] = True
        m["congestion"] = 0.9
        m["indoor"] = True
        m["rate_sub6_mbps"] = 0.4
        m["rate_fr2_mbps"] = 0.0
    elif failure == "recovery":
        m["fr2_blockage"] = False
        m["congestion"] = 0.15
        m["sinr_sub6_db"] = 14.0
        m["sinr_fr2_db"] = 16.0
    return m


def run_policy_on_failure(policy: str, failure: str, seeds: list[int], device_id: str, workload: str) -> dict[str, Any]:
    useful: list[float] = []
    switches: list[float] = []
    interrupt: list[float] = []
    outage: list[float] = []
    defaults = continuity_context_defaults(device_id, workload)
    for seed in seeds:
        rng = np.random.default_rng(int(seed) + 17)
        prev = None
        u = sw = ir = ou = 0.0
        n = 8
        for t in range(n):
            m = _measurements(failure, rng)
            m["min_useful_mbps"] = defaults["min_useful_mbps"]
            m["delay_budget_ms"] = defaults["delay_budget_ms"]
            m["compute_placement"] = defaults["compute_placement"] if m.get("compute_placement") != "unavailable" else "unavailable"
            fam = list(defaults["available_families"])
            ctx = RadioDecisionContext(
                device_class=device_id,
                workload=workload,
                available_families=fam,
                measurements=m,
                twin_hint={"indoor": m.get("indoor"), "predicted_blockage": m.get("fr2_blockage"), "fr2_los": not m.get("fr2_blockage")},
                previous=prev,
                seed=int(seed) * 10 + t,
            )
            if not fam:
                continue
            dec = decide(policy, ctx)
            prev = dec
            u += 1.0 if dec.min_useful_service else 0.0
            sw += float(dec.costs.get("switched", 0.0))
            ir += float(dec.costs.get("interruption_ms", 0.0))
            ou += float(dec.costs.get("outage", 0.0))
        useful.append(u / n)
        switches.append(sw / n)
        interrupt.append(ir / n)
        outage.append(ou / n)
    return {
        "policy": policy,
        "failure": failure,
        "device": device_id,
        "workload": workload,
        "min_useful_service_rate": mean_ci(useful),
        "switch_rate": mean_ci(switches),
        "interruption_ms": mean_ci(interrupt),
        "outage_rate": mean_ci(outage),
        "evidence_class": "SYNTHETIC_SIM",
        "rf_measured": False,
    }


def run_programme(*, heldout: bool = False) -> dict[str, Any]:
    proto = load_dual_protocol()
    seeds = list((proto.get("split") or {}).get("held_out_seeds" if heldout else "seeds"))
    if not heldout:
        seeds = seeds[:3]
    policies = list(proto["policies"])
    failures = ["nominal"] + list(proto["failure_families"])
    devices = list(proto["device_classes"])
    workloads = list(proto["workloads"])
    rows = []
    # Full cartesian is large; CI/held-out uses a structured subset plus one full policy×failure on Student/lecture.
    for policy in policies:
        for failure in failures:
            rows.append(run_policy_on_failure(policy, failure, seeds, "student_14_5", "lecture_video"))
    for device_id in devices:
        for wl in (workloads[0], workloads[1]):
            rows.append(run_policy_on_failure("SERVICE_AWARE_POLICY", "nominal", seeds, device_id, wl))
            rows.append(run_policy_on_failure("SERVICE_AWARE_POLICY", "simultaneous", seeds, device_id, wl))
    # Sequential learned policy training (small).
    from sim.access.radio_decision import RadioDecisionContext as RDC

    scenarios = []
    rng = np.random.default_rng(0)
    for failure in ("nominal", "fr2_blockage", "sub6_congestion", "indoor"):
        m = _measurements(failure, rng)
        scenarios.append(
            RDC(
                device_class="student_14_5",
                workload="lecture_video",
                available_families=["SUB6", "FR2"],
                measurements=m,
                seed=1,
            )
        )
    seq = train_sequential(scenarios, seed=0, epochs=3)
    # Trainable GNN vs heuristic on a tiny multi-BS draw.
    tx = dft_codebook(8, 8)
    rx = dft_codebook(8, 8)
    Hs_ep = [[rng.normal(size=(8, 8)) + 1j * rng.normal(size=(8, 8)) for _ in range(3)] for _ in range(4)]
    model = train_on_oracle(Hs_ep, tx, rx, seed=0, steps=4)
    gnn_trained = run_trainable(Hs_ep, tx, rx, model)
    return {
        "experiment_id": proto["experiment_id"],
        "heldout": heldout,
        "evidence_class": "SYNTHETIC_SIM",
        "latency_class": "HOST_PROCESS_TIMING",
        "sub_ms_inference_proven": False,
        "carriers": proto["carriers"],
        "rows": rows,
        "gnn_audit": classify_existing_gnn(),
        "rl_audit": classify_rl(),
        "gnn_trained": gnn_trained,
        "sequential_policy_weights_shape": list(seq.w.shape),
        "negative_results_valid": True,
        "never": "28 GHz as Sub-6; fabricated RF; Sionna as OTA",
    }


def write_bundle(bundle: dict[str, Any], heldout: bool) -> Path:
    out = ROOT / "results" / "experiments"
    out.mkdir(parents=True, exist_ok=True)
    name = "rq2_dualband_heldout.json" if heldout else "rq2_dualband_train.json"
    path = out / name
    path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    return path
