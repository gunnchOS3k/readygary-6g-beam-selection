#!/usr/bin/env python3
"""Run additive Paper II arms AFTER experiment_protocol_additive.yaml exists."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sim.channels import availability_report, get_backend  # noqa: E402
from sim.experiments.digital_programme import (  # noqa: E402
    dft_codebook,
    exhaustive,
    load_protocol,
    mean_ci,
    run_family,
)
from sim.models.gnn_multi_bs import run_multi_bs_episode  # noqa: E402
from sim.policies.adaptive_tracking import TRACKERS, run_tracker_episode  # noqa: E402

ADD_REL = Path("paper/artifacts/experiment_protocol_additive.yaml")


def _draw_episode(backend, proto, rng, n_slots: int, family: str):
    from sim.experiments.digital_programme import ChannelSlot

    slots = []
    Hs_seq = []
    n_bs = int((proto.get("split") or {}).get("n_bs", 3))
    for _ in range(n_slots):
        draws = [backend.draw(rng, proto, family) for _ in range(n_bs)]
        slots.append(ChannelSlot(H=draws[0].H, aoa=draws[0].aoa, aod=draws[0].aod, family=family))
        Hs_seq.append([d.H for d in draws])
    return slots, Hs_seq


def run_additive(include_heldout: bool) -> dict:
    proto = load_protocol(ROOT / ADD_REL)
    assert proto["carrier"]["frequency_hz"] == 28_000_000_000
    assert proto["carrier"]["band"] == "FR2"
    ch = proto["channel"]
    tx_cb = dft_codebook(int(ch["num_tx_beams"]), int(ch["num_tx_ant"]))
    rx_cb = dft_codebook(int(ch["num_rx_beams"]), int(ch["num_rx_ant"]))
    split = proto["split"]
    n_ep = int(split["n_episodes_per_seed"])
    n_slots = int(split["n_slots_per_episode"])
    avail = availability_report()
    seeds = list(split["held_out_seeds"] if include_heldout else split["train_seeds"])
    family = "held_out" if include_heldout else "in_distribution"

    channel_rows = {}
    for bname in proto["channel_backends"]:
        be = get_backend(bname)
        ok, reason = be.available()
        snrs = []
        for seed in seeds:
            rng = __import__("numpy").random.default_rng(int(seed))
            ep_snr = []
            for _ in range(n_ep):
                slots, _ = _draw_episode(be, proto, rng, n_slots, "in_distribution")
                vals = [exhaustive(s.H, tx_cb, rx_cb)[2] for s in slots]
                ep_snr.append(sum(vals) / len(vals))
            snrs.append(sum(ep_snr) / len(ep_snr))
        channel_rows[bname] = {
            "available": ok,
            "reason": reason,
            "evidence_class": be.evidence_class,
            "oracle_mean_snr_linear": mean_ci(snrs),
            "ota": False,
        }

    gnn_rows = {}
    for mode in ("independent_multi_bs", "gnn_multi_bs", "gnn_no_message"):
        metric_lists: dict[str, list[float]] = {}
        be = get_backend("tdl_a")
        for seed in seeds:
            rng = __import__("numpy").random.default_rng(int(seed))
            ep_rows = []
            for _ in range(n_ep):
                _, Hs_seq = _draw_episode(be, proto, rng, n_slots, "in_distribution")
                ep_rows.append(run_multi_bs_episode(Hs_seq, tx_cb, rx_cb, mode))
            for k in ep_rows[0]:
                metric_lists.setdefault(k, []).append(sum(r[k] for r in ep_rows) / len(ep_rows))
        gnn_rows[mode] = {k: mean_ci(v) for k, v in metric_lists.items()}

    adaptive_rows = {}
    be = get_backend("tdl_c")
    for name in TRACKERS:
        metric_lists = {}
        for seed in seeds:
            rng = __import__("numpy").random.default_rng(int(seed))
            ep_rows = []
            for _ in range(n_ep):
                slots, _ = _draw_episode(be, proto, rng, n_slots, "in_distribution")
                ep_rows.append(
                    run_tracker_episode(
                        slots,
                        name,
                        tx_cb,
                        rx_cb,
                        rng=rng,
                        probe_budget=int((proto.get("costs") or {}).get("probe_budget_default", 2)),
                        switch_penalty_db=float((proto.get("costs") or {}).get("beam_switch_penalty_db", 0.25)),
                    )
                )
            for k in ep_rows[0]:
                metric_lists.setdefault(k, []).append(sum(r[k] for r in ep_rows) / len(ep_rows))
        adaptive_rows[name] = {k: mean_ci(v) for k, v in metric_lists.items()}

    # Probe-budget ablation (bandit + constrained RL).
    probe_ablation = {}
    for budget in (1, 4):
        probe_ablation[budget] = {}
        for name in ("adaptive_bandit", "adaptive_constrained_rl"):
            vals = []
            for seed in seeds:
                rng = __import__("numpy").random.default_rng(int(seed))
                ep = []
                for _ in range(n_ep):
                    slots, _ = _draw_episode(be, proto, rng, n_slots, "in_distribution")
                    ep.append(
                        run_tracker_episode(
                            slots, name, tx_cb, rx_cb, rng=rng, probe_budget=budget, switch_penalty_db=0.25
                        )["mean_snr_db"]
                    )
                vals.append(sum(ep) / len(ep))
            probe_ablation[budget][name] = mean_ci(vals)

    # Keep original programme family on synthetic for twin vs info-equivalent comparison.
    core = run_family(
        proto,
        family=family if family != "held_out" else "in_distribution",
        seeds=seeds,
        policies=["no_adaptation", "twin_informed", "information_equivalent", "exhaustive_oracle"],
    )

    bundle = {
        "experiment_id": proto["experiment_id"],
        "evidence_class": "SYNTHETIC_SIM",
        "latency_class": "HOST_PROCESS_TIMING",
        "sub_ms_inference_proven": False,
        "sub_ms_inference_target": True,
        "carrier_frequency_hz": 28000000000,
        "band": "FR2",
        "never": "Sub-6",
        "held_out_generated": include_heldout,
        "channel_availability": avail,
        "channel_oracle": channel_rows,
        "gnn_multi_bs": gnn_rows,
        "adaptive_tracking": adaptive_rows,
        "probe_budget_ablation": probe_ablation,
        "twin_vs_info": core,
        "ota": False,
    }
    out = ROOT / "results" / "experiments"
    out.mkdir(parents=True, exist_ok=True)
    name = f"{proto['experiment_id']}_{'heldout' if include_heldout else 'train'}.json"
    (out / name).write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    return bundle


def main() -> int:
    include = "--heldout" in sys.argv
    bundle = run_additive(include_heldout=include)
    print(json.dumps({"wrote": bundle["experiment_id"], "heldout": include, "band": "FR2"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
