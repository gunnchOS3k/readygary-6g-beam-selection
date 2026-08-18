"""Adaptive beam tracking: static / heuristic / opt / bandit / constrained RL.

Probe budget and switching cost are first-class. Negative results are kept.
HOST_PROCESS_TIMING only. SYNTHETIC_SIM. Not OTA.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from sim.experiments.digital_programme import (
    BeamAction,
    ChannelSlot,
    beam_snr,
    exhaustive,
    hierarchical,
    window_search,
)


@dataclass
class TrackerState:
    prev: BeamAction | None = None
    probes_used: int = 0
    q: dict[tuple[int, int], float] | None = None
    counts: dict[tuple[int, int], int] | None = None


def _switch_cost(prev: BeamAction | None, action: BeamAction, penalty_db: float) -> float:
    if prev is None:
        return 0.0
    if prev.tx_idx == action.tx_idx and prev.rx_idx == action.rx_idx:
        return 0.0
    return penalty_db


def adaptive_static(slot: ChannelSlot, st: TrackerState, tx_cb, rx_cb, **_: object) -> BeamAction:
    if st.prev is None:
        ti, ri, s = exhaustive(slot.H, tx_cb, rx_cb)
        return BeamAction(ti, ri, s, "adaptive_static_lock")
    s = beam_snr(slot.H, tx_cb, rx_cb, st.prev.tx_idx, st.prev.rx_idx)
    return BeamAction(st.prev.tx_idx, st.prev.rx_idx, s, "adaptive_static")


def adaptive_heuristic(slot: ChannelSlot, st: TrackerState, tx_cb, rx_cb, **kw: object) -> BeamAction:
    drop_db = float(kw.get("drop_db", 3.0))
    if st.prev is None:
        ti, ri, s = window_search(slot.H, tx_cb, rx_cb, 0, 0, 2)
        return BeamAction(ti, ri, s, "adaptive_heuristic_init")
    held = beam_snr(slot.H, tx_cb, rx_cb, st.prev.tx_idx, st.prev.rx_idx)
    drop = 10.0 * math.log10(max(st.prev.snr_linear, 1e-18) / max(held, 1e-18))
    if drop <= drop_db:
        return BeamAction(st.prev.tx_idx, st.prev.rx_idx, held, "adaptive_heuristic_hold")
    ti, ri, s = window_search(slot.H, tx_cb, rx_cb, st.prev.tx_idx, st.prev.rx_idx, 2)
    return BeamAction(ti, ri, s, "adaptive_heuristic_research")


def adaptive_opt(slot: ChannelSlot, st: TrackerState, tx_cb, rx_cb, **_: object) -> BeamAction:
    _ = st
    ti, ri, s = hierarchical(slot.H, tx_cb, rx_cb, coarse_factor=2)
    return BeamAction(ti, ri, s, "adaptive_opt")


def adaptive_bandit(
    slot: ChannelSlot,
    st: TrackerState,
    tx_cb,
    rx_cb,
    *,
    rng: np.random.Generator,
    probe_budget: int = 2,
    epsilon: float = 0.15,
    **_: object,
) -> BeamAction:
    n_tx, n_rx = tx_cb.shape[0], rx_cb.shape[0]
    if st.q is None:
        st.q = {(t, r): 0.0 for t in range(n_tx) for r in range(n_rx)}
        st.counts = dict.fromkeys(st.q, 0)
    pairs = list(st.q.keys())
    if st.probes_used < probe_budget and float(rng.random()) < epsilon:
        t, r = pairs[int(rng.integers(0, len(pairs)))]
        st.probes_used += 1
        s = beam_snr(slot.H, tx_cb, rx_cb, t, r)
        n = st.counts[(t, r)] + 1
        st.counts[(t, r)] = n
        st.q[(t, r)] += (s - st.q[(t, r)]) / n
        return BeamAction(t, r, s, "adaptive_bandit_probe")
    t, r = max(st.q, key=st.q.get)
    s = beam_snr(slot.H, tx_cb, rx_cb, t, r)
    n = st.counts[(t, r)] + 1
    st.counts[(t, r)] = n
    st.q[(t, r)] += (s - st.q[(t, r)]) / n
    return BeamAction(t, r, s, "adaptive_bandit_exploit")


def adaptive_constrained_rl(
    slot: ChannelSlot,
    st: TrackerState,
    tx_cb,
    rx_cb,
    *,
    rng: np.random.Generator,
    probe_budget: int = 2,
    switch_penalty_db: float = 0.25,
    **_: object,
) -> BeamAction:
    """Tabular Q with switch penalty. Constrained by probe_budget per episode."""
    n_tx, n_rx = tx_cb.shape[0], rx_cb.shape[0]
    if st.q is None:
        st.q = {(t, r): 0.0 for t in range(n_tx) for r in range(n_rx)}
        st.counts = dict.fromkeys(st.q, 0)
    # Candidate set: previous pair + up to probe_budget random neighbors.
    candidates = []
    if st.prev is not None:
        candidates.append((st.prev.tx_idx, st.prev.rx_idx))
    while len(candidates) < 1 + probe_budget:
        t = int(rng.integers(0, n_tx))
        r = int(rng.integers(0, n_rx))
        if (t, r) not in candidates:
            candidates.append((t, r))
            st.probes_used += 1
    best_pair = candidates[0]
    best_q = -1e18
    for t, r in candidates:
        s = beam_snr(slot.H, tx_cb, rx_cb, t, r)
        penalty = 0.0
        if st.prev is not None and (t != st.prev.tx_idx or r != st.prev.rx_idx):
            penalty = switch_penalty_db
        reward = 10.0 * math.log10(max(s, 1e-18)) - penalty
        n = st.counts[(t, r)] + 1
        st.counts[(t, r)] = n
        st.q[(t, r)] += (reward - st.q[(t, r)]) / n
        if st.q[(t, r)] > best_q:
            best_q = st.q[(t, r)]
            best_pair = (t, r)
    t, r = best_pair
    s = beam_snr(slot.H, tx_cb, rx_cb, t, r)
    return BeamAction(t, r, s, "adaptive_constrained_rl")


TRACKERS = {
    "adaptive_static": adaptive_static,
    "adaptive_heuristic": adaptive_heuristic,
    "adaptive_opt": adaptive_opt,
    "adaptive_bandit": adaptive_bandit,
    "adaptive_constrained_rl": adaptive_constrained_rl,
}


def run_tracker_episode(
    slots: list[ChannelSlot],
    name: str,
    tx_cb: np.ndarray,
    rx_cb: np.ndarray,
    *,
    rng: np.random.Generator,
    probe_budget: int = 2,
    switch_penalty_db: float = 0.25,
) -> dict[str, float]:
    fn = TRACKERS[name]
    st = TrackerState()
    snrs = []
    n_sw = 0
    switch_cost = 0.0
    for slot in slots:
        kw = {
            "rng": rng,
            "probe_budget": probe_budget,
            "switch_penalty_db": switch_penalty_db,
        }
        action = fn(slot, st, tx_cb, rx_cb, **kw)
        switch_cost += _switch_cost(st.prev, action, switch_penalty_db)
        if st.prev is not None and (action.tx_idx != st.prev.tx_idx or action.rx_idx != st.prev.rx_idx):
            n_sw += 1
        snrs.append(action.snr_linear)
        st.prev = action
    mean_lin = float(sum(snrs) / max(len(snrs), 1))
    return {
        "mean_snr_linear": mean_lin,
        "mean_snr_db": 10.0 * math.log10(max(mean_lin, 1e-18)),
        "n_beam_switches": float(n_sw),
        "switch_cost": switch_cost,
        "probes_used": float(st.probes_used),
        "probe_budget": float(probe_budget),
    }
