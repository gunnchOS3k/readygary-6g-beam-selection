"""Paper II FR2 mmWave beam digital programme.

SYNTHETIC_SIM TDL draws at 28e9 Hz (FR2, 3GPP TS 38.101-2). Never Sub-6.
compute_time_ms is HOST_PROCESS_TIMING, not measured RF / gNB slot / ONNX.
"""
from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np

PROTOCOL_RELPATH = Path("paper/artifacts/experiment_protocol.yaml")
C_LIGHT = 299792458.0

T_CRIT_975 = {
    1: 12.706,
    2: 4.303,
    3: 3.182,
    4: 2.776,
    5: 2.571,
    6: 2.447,
    7: 2.365,
    8: 2.306,
    9: 2.262,
    10: 2.228,
}


def _mini_yaml_load(text: str) -> Any:
    def parse_scalar(raw: str) -> Any:
        s = raw.strip()
        if s in ("true", "True"):
            return True
        if s in ("false", "False"):
            return False
        if s in ("null", "~"):
            return None
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return s[1:-1]
        if s.startswith("[") and s.endswith("]"):
            inner = s[1:-1].strip()
            if not inner:
                return []
            return [parse_scalar(p) for p in inner.split(",")]
        try:
            if "." in s or "e" in s.lower():
                return float(s)
            return int(s)
        except ValueError:
            return s

    cleaned: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if " #" in raw:
            raw = raw.split(" #", 1)[0].rstrip()
        cleaned.append(raw.rstrip())

    def indent(line: str) -> int:
        return len(line) - len(line.lstrip(" "))

    def parse_block(i: int, base: int) -> tuple[Any, int]:
        if i >= len(cleaned) or indent(cleaned[i]) < base:
            return {}, i
        if cleaned[i].lstrip().startswith("- "):
            items: list[Any] = []
            while i < len(cleaned) and indent(cleaned[i]) == base and cleaned[i].lstrip().startswith("- "):
                items.append(parse_scalar(cleaned[i].lstrip()[2:]))
                i += 1
            return items, i
        mapping: dict[str, Any] = {}
        while i < len(cleaned) and indent(cleaned[i]) == base and not cleaned[i].lstrip().startswith("- "):
            line = cleaned[i].lstrip()
            if ":" not in line:
                i += 1
                continue
            key, _, rest = line.partition(":")
            key = key.strip()
            rest = rest.strip()
            if rest in (">", "|"):
                folded: list[str] = []
                i += 1
                while i < len(cleaned) and indent(cleaned[i]) > base:
                    folded.append(cleaned[i].strip())
                    i += 1
                mapping[key] = " ".join(folded)
                continue
            if rest:
                mapping[key] = parse_scalar(rest)
                i += 1
                continue
            if i + 1 < len(cleaned) and indent(cleaned[i + 1]) > base:
                child, i = parse_block(i + 1, indent(cleaned[i + 1]))
                mapping[key] = child
            else:
                mapping[key] = {}
                i += 1
        return mapping, i

    doc, _ = parse_block(0, indent(cleaned[0]) if cleaned else 0)
    return doc


def load_protocol(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
    except Exception:
        data = _mini_yaml_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"Protocol is not a mapping: {path}")
    if data.get("frozen") is not True:
        raise ValueError("Protocol must set frozen: true")
    carrier = data.get("carrier") or {}
    if int(carrier.get("frequency_hz", 0)) != 28_000_000_000:
        raise ValueError("Protocol carrier.frequency_hz must be 28000000000 (FR2)")
    if str(carrier.get("band")) != "FR2":
        raise ValueError("28 GHz must be labelled FR2, not Sub-6")
    return data


def t_crit_975(df: int) -> float:
    if df <= 0:
        return float("nan")
    return float(T_CRIT_975.get(df, 1.96))


def mean_ci(values: list[float]) -> dict[str, float]:
    arr = [float(v) for v in values]
    n = len(arr)
    if n == 0:
        return {"n": 0, "mean": float("nan"), "ci_low": float("nan"), "ci_high": float("nan"), "sd": float("nan")}
    m = float(sum(arr) / n)
    if n == 1:
        return {"n": 1, "mean": m, "ci_low": m, "ci_high": m, "sd": 0.0}
    var = sum((x - m) ** 2 for x in arr) / (n - 1)
    sd = math.sqrt(var)
    half = t_crit_975(n - 1) * sd / math.sqrt(n)
    return {"n": n, "mean": m, "ci_low": m - half, "ci_high": m + half, "sd": sd}


def cohens_d(a: list[float], b: list[float]) -> float:
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    va = sum((x - ma) ** 2 for x in a) / (len(a) - 1)
    vb = sum((x - mb) ** 2 for x in b) / (len(b) - 1)
    pooled = math.sqrt(((len(a) - 1) * va + (len(b) - 1) * vb) / (len(a) + len(b) - 2))
    if pooled == 0:
        return 0.0
    return (ma - mb) / pooled


def dft_codebook(n_beams: int, n_ant: int) -> np.ndarray:
    beams = np.arange(n_beams)[:, None]
    ants = np.arange(n_ant)[None, :]
    return np.exp(1j * 2 * np.pi * beams * ants / n_beams) / np.sqrt(n_ant)


def beam_snr(H: np.ndarray, tx_cb: np.ndarray, rx_cb: np.ndarray, tx_idx: int, rx_idx: int) -> float:
    val = tx_cb[tx_idx] @ H @ rx_cb[rx_idx]
    return float(np.abs(val) ** 2)


def aoa_to_beam_index(aoa: float, n_beams: int) -> int:
    idx = int(np.round((n_beams - 1) * (np.cos(aoa) + 1.0) / 2.0))
    return int(np.clip(idx, 0, n_beams - 1))


@dataclass
class ChannelSlot:
    H: np.ndarray
    aoa: float
    aod: float
    family: str


def generate_slot(
    rng: np.random.Generator,
    proto: dict[str, Any],
    family: str,
    *,
    ablation: str = "full",
) -> ChannelSlot:
    ch = proto["channel"]
    n_tx = int(ch["num_tx_ant"])
    n_rx = int(ch["num_rx_ant"])
    freq = float((proto.get("carrier") or {}).get("frequency_hz", 28e9))
    _ = freq  # labelled FR2; used as documentation of the draw, not a Sub-6 model
    if family == "high_blockage":
        lo, hi = ch["path_count_high_blockage"]
        atten = 0.35
    else:
        lo, hi = ch["path_count_in_distribution"]
        atten = 1.0
    if ablation == "no_mobility":
        mobility = 0.0
    else:
        mobility = float(ch.get("mobility_scale_high_mobility" if family == "high_mobility" else "mobility_scale_in_distribution", 1.0))
    n_paths = int(rng.integers(int(lo), int(hi) + 1))
    H = np.zeros((n_tx, n_rx), dtype=np.complex128)
    aoa0 = float(rng.uniform(0.0, np.pi))
    aod0 = float(rng.uniform(0.0, np.pi))
    for p in range(n_paths):
        aoa = aoa0 + mobility * float(rng.normal(0.0, 0.15 if p else 0.02))
        aod = aod0 + mobility * float(rng.normal(0.0, 0.15 if p else 0.02))
        gain = float(rng.exponential(1.0)) * atten * (1.0 if p == 0 else 0.45)
        phase = float(rng.uniform(0.0, 2 * np.pi))
        tx_sv = np.exp(1j * np.pi * np.arange(n_tx) * np.cos(aod)) / np.sqrt(n_tx)
        rx_sv = np.exp(1j * np.pi * np.arange(n_rx) * np.cos(aoa)) / np.sqrt(n_rx)
        H += gain * np.exp(1j * phase) * np.outer(tx_sv, rx_sv)
    return ChannelSlot(H=H, aoa=aoa0, aod=aod0, family=family)


def exhaustive(H: np.ndarray, tx_cb: np.ndarray, rx_cb: np.ndarray) -> tuple[int, int, float]:
    best_tx = 0
    best_rx = 0
    best = -1.0
    for ti in range(tx_cb.shape[0]):
        for ri in range(rx_cb.shape[0]):
            s = beam_snr(H, tx_cb, rx_cb, ti, ri)
            if s > best:
                best = s
                best_tx, best_rx = ti, ri
    return best_tx, best_rx, best


def hierarchical(H: np.ndarray, tx_cb: np.ndarray, rx_cb: np.ndarray, coarse_factor: int = 2) -> tuple[int, int, float]:
    n_tx = tx_cb.shape[0]
    n_rx = rx_cb.shape[0]
    step_t = max(1, n_tx // max(coarse_factor, 1))
    step_r = max(1, n_rx // max(coarse_factor, 1))
    best_tx = 0
    best_rx = 0
    best = -1.0
    for ti in range(0, n_tx, step_t):
        for ri in range(0, n_rx, step_r):
            s = beam_snr(H, tx_cb, rx_cb, ti, ri)
            if s > best:
                best = s
                best_tx, best_rx = ti, ri
    window = 2
    t0, t1 = max(0, best_tx - window), min(n_tx, best_tx + window + 1)
    r0, r1 = max(0, best_rx - window), min(n_rx, best_rx + window + 1)
    for ti in range(t0, t1):
        for ri in range(r0, r1):
            s = beam_snr(H, tx_cb, rx_cb, ti, ri)
            if s > best:
                best = s
                best_tx, best_rx = ti, ri
    return best_tx, best_rx, best


def window_search(
    H: np.ndarray,
    tx_cb: np.ndarray,
    rx_cb: np.ndarray,
    tx_c: int,
    rx_c: int,
    window: int,
) -> tuple[int, int, float]:
    n_tx, n_rx = tx_cb.shape[0], rx_cb.shape[0]
    best_tx, best_rx = tx_c, rx_c
    best = beam_snr(H, tx_cb, rx_cb, tx_c, rx_c)
    for ti in range(max(0, tx_c - window), min(n_tx, tx_c + window + 1)):
        for ri in range(max(0, rx_c - window), min(n_rx, rx_c + window + 1)):
            s = beam_snr(H, tx_cb, rx_cb, ti, ri)
            if s > best:
                best = s
                best_tx, best_rx = ti, ri
    return best_tx, best_rx, best


@dataclass
class BeamAction:
    tx_idx: int
    rx_idx: int
    snr_linear: float
    rationale: str


def policy_no_adaptation(slot: ChannelSlot, prev: BeamAction | None, tx_cb, rx_cb, proto, ablation: str) -> BeamAction:
    _ = prev, proto, ablation
    s = beam_snr(slot.H, tx_cb, rx_cb, 0, 0)
    return BeamAction(0, 0, s, "no_adaptation")


def policy_local_only(slot: ChannelSlot, prev: BeamAction | None, tx_cb, rx_cb, proto, ablation: str) -> BeamAction:
    _ = prev, proto, ablation
    best_rx = 0
    best = -1.0
    for ri in range(rx_cb.shape[0]):
        s = beam_snr(slot.H, tx_cb, rx_cb, 0, ri)
        if s > best:
            best = s
            best_rx = ri
    return BeamAction(0, best_rx, best, "local_only")


def policy_cloud_only(slot: ChannelSlot, prev: BeamAction | None, tx_cb, rx_cb, proto, ablation: str) -> BeamAction:
    _ = prev, proto, ablation
    ti, ri, s = exhaustive(slot.H, tx_cb, rx_cb)
    return BeamAction(ti, ri, s, "cloud_only")


def policy_edge_only(slot: ChannelSlot, prev: BeamAction | None, tx_cb, rx_cb, proto, ablation: str) -> BeamAction:
    _ = prev, proto
    factor = 4 if ablation == "reduced_codebook" else 2
    ti, ri, s = hierarchical(slot.H, tx_cb, rx_cb, coarse_factor=factor)
    return BeamAction(ti, ri, s, "edge_only")


def policy_rule_based(slot: ChannelSlot, prev: BeamAction | None, tx_cb, rx_cb, proto, ablation: str) -> BeamAction:
    _ = proto, ablation
    if prev is None:
        ti, ri, s = window_search(slot.H, tx_cb, rx_cb, 0, 0, 2)
        return BeamAction(ti, ri, s, "rule_based")
    held = beam_snr(slot.H, tx_cb, rx_cb, prev.tx_idx, prev.rx_idx)
    drop_db = 10.0 * math.log10(max(prev.snr_linear, 1e-18) / max(held, 1e-18))
    if drop_db <= 3.0:
        return BeamAction(prev.tx_idx, prev.rx_idx, held, "rule_based_hold")
    ti, ri, s = window_search(slot.H, tx_cb, rx_cb, prev.tx_idx, prev.rx_idx, 1)
    return BeamAction(ti, ri, s, "rule_based_research")


def policy_optimization_based(slot: ChannelSlot, prev: BeamAction | None, tx_cb, rx_cb, proto, ablation: str) -> BeamAction:
    act = policy_edge_only(slot, prev, tx_cb, rx_cb, proto, ablation)
    act.rationale = "optimization_based"
    return act


def policy_twin_informed(slot: ChannelSlot, prev: BeamAction | None, tx_cb, rx_cb, proto, ablation: str) -> BeamAction:
    _ = prev, proto
    if ablation == "no_aoa_hint":
        ti, ri, s = hierarchical(slot.H, tx_cb, rx_cb, coarse_factor=2)
        return BeamAction(ti, ri, s, "twin_informed_no_aoa")
    tx_c = aoa_to_beam_index(slot.aod, tx_cb.shape[0])
    rx_c = aoa_to_beam_index(slot.aoa, rx_cb.shape[0])
    window = 1 if ablation == "reduced_codebook" else 2
    ti, ri, s = window_search(slot.H, tx_cb, rx_cb, tx_c, rx_c, window)
    return BeamAction(ti, ri, s, "twin_informed")


def policy_information_equivalent(slot: ChannelSlot, prev: BeamAction | None, tx_cb, rx_cb, proto, ablation: str) -> BeamAction:
    """Same AoA hint as twin_informed; nearest DFT bin, no neighbor search."""
    _ = prev, proto
    if ablation == "no_aoa_hint":
        s = beam_snr(slot.H, tx_cb, rx_cb, 0, 0)
        return BeamAction(0, 0, s, "information_equivalent_no_aoa")
    ti = aoa_to_beam_index(slot.aod, tx_cb.shape[0])
    ri = aoa_to_beam_index(slot.aoa, rx_cb.shape[0])
    s = beam_snr(slot.H, tx_cb, rx_cb, ti, ri)
    return BeamAction(ti, ri, s, "information_equivalent")


def policy_exhaustive_oracle(slot: ChannelSlot, prev: BeamAction | None, tx_cb, rx_cb, proto, ablation: str) -> BeamAction:
    _ = prev, proto, ablation
    ti, ri, s = exhaustive(slot.H, tx_cb, rx_cb)
    return BeamAction(ti, ri, s, "exhaustive_oracle")


POLICIES: dict[str, Callable[..., BeamAction]] = {
    "no_adaptation": policy_no_adaptation,
    "local_only": policy_local_only,
    "cloud_only": policy_cloud_only,
    "edge_only": policy_edge_only,
    "rule_based": policy_rule_based,
    "optimization_based": policy_optimization_based,
    "twin_informed": policy_twin_informed,
    "information_equivalent": policy_information_equivalent,
    "exhaustive_oracle": policy_exhaustive_oracle,
}


def snr_db(linear: float) -> float:
    return 10.0 * math.log10(max(linear, 1e-18))


def run_policy_on_episode(
    slots: list[ChannelSlot],
    policy_name: str,
    proto: dict[str, Any],
    tx_cb: np.ndarray,
    rx_cb: np.ndarray,
    ablation: str,
) -> dict[str, float]:
    switch_pen = float((proto.get("costs") or {}).get("beam_switch_penalty_db", 0.25))
    prev: BeamAction | None = None
    frozen: BeamAction | None = None
    oracle_snrs: list[float] = []
    pred_snrs: list[float] = []
    top1 = 0
    n_sw = 0
    compute_ms = 0.0
    fn = POLICIES["exhaustive_oracle"] if policy_name == "static" else POLICIES[policy_name]
    for slot in slots:
        o_tx, o_rx, o_s = exhaustive(slot.H, tx_cb, rx_cb)
        oracle_snrs.append(o_s)
        t0 = time.perf_counter()
        if policy_name == "static":
            if frozen is None:
                ti, ri, s = exhaustive(slot.H, tx_cb, rx_cb)
                frozen = BeamAction(ti, ri, s, "static")
            # Re-evaluate frozen pair on current H (no new search after slot 0).
            s_now = beam_snr(slot.H, tx_cb, rx_cb, frozen.tx_idx, frozen.rx_idx)
            action = BeamAction(frozen.tx_idx, frozen.rx_idx, s_now, "static")
        else:
            action = fn(slot, prev, tx_cb, rx_cb, proto, ablation)
        compute_ms += (time.perf_counter() - t0) * 1000.0
        pred_snrs.append(action.snr_linear)
        if action.tx_idx == o_tx and action.rx_idx == o_rx:
            top1 += 1
        if prev is not None and (action.tx_idx != prev.tx_idx or action.rx_idx != prev.rx_idx):
            n_sw += 1
        prev = action
    mean_lin = float(sum(pred_snrs) / len(pred_snrs))
    mean_or = float(sum(oracle_snrs) / len(oracle_snrs))
    return {
        "mean_snr_linear": mean_lin,
        "mean_snr_db": snr_db(mean_lin),
        "db_loss_vs_oracle": max(0.0, snr_db(mean_or) - snr_db(mean_lin)),
        "top1_match_oracle": float(top1 / len(slots)),
        "n_beam_switches": float(n_sw),
        "switch_cost": float(n_sw) * switch_pen,
        "compute_time_ms": float(compute_ms),
    }


def run_family(
    proto: dict[str, Any],
    *,
    family: str,
    seeds: list[int],
    policies: list[str] | None = None,
    ablation: str = "full",
) -> dict[str, Any]:
    split = proto["split"]
    ch = proto["channel"]
    n_ep = int(split["n_episodes_per_seed"])
    n_slots = int(split["n_slots_per_episode"])
    policies = policies or list(proto["policies"])
    n_tx_b = int(ch["num_tx_beams"])
    n_rx_b = int(ch["num_rx_beams"])
    if ablation == "reduced_codebook":
        n_tx_b = max(4, n_tx_b // 2)
        n_rx_b = max(4, n_rx_b // 2)
    tx_cb = dft_codebook(n_tx_b, int(ch["num_tx_ant"]))
    rx_cb = dft_codebook(n_rx_b, int(ch["num_rx_ant"]))
    per_policy: dict[str, dict[str, list[float]]] = {p: {} for p in policies}
    for seed in seeds:
        rng = np.random.default_rng(int(seed))
        episodes = [[generate_slot(rng, proto, family, ablation=ablation) for _ in range(n_slots)] for _ in range(n_ep)]
        for policy in policies:
            if policy != "static" and policy not in POLICIES:
                raise ValueError(f"Unknown policy {policy}")
            ep_rows = [run_policy_on_episode(ep, policy, proto, tx_cb, rx_cb, ablation) for ep in episodes]
            for k in ep_rows[0]:
                per_policy[policy].setdefault(k, []).append(float(sum(r[k] for r in ep_rows) / len(ep_rows)))
    summaries = {}
    for policy, metric_map in per_policy.items():
        summaries[policy] = {metric: mean_ci(vals) for metric, vals in metric_map.items()}
        summaries[policy]["seed_means"] = metric_map
    baseline = per_policy.get("no_adaptation", {})
    effects = {}
    if "mean_snr_db" in baseline:
        base_vals = baseline["mean_snr_db"]
        for policy, metric_map in per_policy.items():
            effects[policy] = {"cohens_d_vs_no_adaptation_snr_db": cohens_d(metric_map["mean_snr_db"], base_vals)}
    return {
        "family": family,
        "ablation": ablation,
        "seeds": list(seeds),
        "n_episodes_per_seed": n_ep,
        "n_slots_per_episode": n_slots,
        "carrier_frequency_hz": int((proto.get("carrier") or {}).get("frequency_hz", 28000000000)),
        "band": (proto.get("carrier") or {}).get("band", "FR2"),
        "policies": summaries,
        "effect_sizes": effects,
        "evidence_class": proto.get("evidence_class", "SYNTHETIC_SIM"),
        "latency_class": proto.get("latency_class", "HOST_PROCESS_TIMING"),
        "sub_ms_inference_proven": False,
    }


def _strip_seed_means(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _strip_seed_means(v) for k, v in obj.items() if k != "seed_means"}
    if isinstance(obj, list):
        return [_strip_seed_means(x) for x in obj]
    return obj


def run_programme(
    repo_root: Path,
    *,
    include_heldout: bool = False,
    include_domain_shift: bool = False,
    include_ablations: bool = False,
) -> dict[str, Any]:
    protocol_path = repo_root / PROTOCOL_RELPATH
    if not protocol_path.is_file():
        raise FileNotFoundError(f"Protocol missing: {protocol_path}")
    proto = load_protocol(protocol_path)
    split = proto["split"]
    out_dir = repo_root / "results" / "experiments"
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle: dict[str, Any] = {
        "experiment_id": proto["experiment_id"],
        "title": proto.get("title"),
        "evidence_class": proto.get("evidence_class"),
        "latency_class": proto.get("latency_class"),
        "sub_ms_inference_proven": False,
        "carrier_frequency_hz": 28000000000,
        "band": "FR2",
        "protocol_path": str(PROTOCOL_RELPATH),
        "held_out_generated": False,
    }
    train = run_family(proto, family="in_distribution", seeds=list(split["train_seeds"]))
    (out_dir / f"{proto['experiment_id']}_train.json").write_text(json.dumps(train, indent=2) + "\n", encoding="utf-8")
    bundle["train"] = train
    if include_heldout:
        held = run_family(proto, family="held_out", seeds=list(split["held_out_seeds"]))
        (out_dir / f"{proto['experiment_id']}_heldout.json").write_text(json.dumps(held, indent=2) + "\n", encoding="utf-8")
        bundle["held_out"] = held
        bundle["held_out_generated"] = True
    if include_domain_shift:
        shifts = {}
        for fam in split.get("domain_shift_families") or []:
            shifts[fam] = run_family(proto, family=str(fam), seeds=list(split["held_out_seeds"]))
        (out_dir / f"{proto['experiment_id']}_domain_shift.json").write_text(json.dumps(shifts, indent=2) + "\n", encoding="utf-8")
        bundle["domain_shift"] = shifts
    if include_ablations:
        ablations = {}
        for name in proto.get("ablations") or []:
            ablations[name] = run_family(
                proto,
                family="held_out",
                seeds=list(split["held_out_seeds"]),
                policies=["twin_informed", "information_equivalent"],
                ablation=str(name),
            )
        (out_dir / f"{proto['experiment_id']}_ablation.json").write_text(json.dumps(ablations, indent=2) + "\n", encoding="utf-8")
        bundle["ablations"] = ablations
    (out_dir / f"{proto['experiment_id']}_summary.json").write_text(json.dumps(_strip_seed_means(bundle), indent=2) + "\n", encoding="utf-8")
    return bundle
