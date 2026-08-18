"""GNN multi-BS experimental arm + independent (non-GNN) baseline + no-message ablation.

Numpy message passing only. Not a PyG/DGL hard dependency. SYNTHETIC_SIM.
Each node is a base station with its own FR2 H. Edges are fully connected.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from sim.experiments.digital_programme import BeamAction, hierarchical, window_search


def independent_multi_bs(
    Hs: list[np.ndarray],
    tx_cb: np.ndarray,
    rx_cb: np.ndarray,
    coarse_factor: int = 2,
) -> list[BeamAction]:
    actions = []
    for H in Hs:
        ti, ri, s = hierarchical(H, tx_cb, rx_cb, coarse_factor=coarse_factor)
        actions.append(BeamAction(ti, ri, s, "independent_multi_bs"))
    return actions


def gnn_multi_bs(
    Hs: list[np.ndarray],
    tx_cb: np.ndarray,
    rx_cb: np.ndarray,
    *,
    message_passing: bool = True,
    coarse_factor: int = 2,
) -> list[BeamAction]:
    local = independent_multi_bs(Hs, tx_cb, rx_cb, coarse_factor=coarse_factor)
    if not message_passing or len(Hs) < 2:
        for a in local:
            a.rationale = "gnn_no_message" if not message_passing else a.rationale
        return local
    # One round: average neighbor DFT bins, then local window refine.
    tx_mean = int(round(sum(a.tx_idx for a in local) / len(local)))
    rx_mean = int(round(sum(a.rx_idx for a in local) / len(local)))
    refined: list[BeamAction] = []
    for H, loc in zip(Hs, local):
        # Residual connection: mix local hierarchical pick with neighbor consensus.
        ti, ri, s = window_search(H, tx_cb, rx_cb, tx_mean, rx_mean, window=2)
        if loc.snr_linear >= s:
            loc.rationale = "gnn_multi_bs_keep_local"
            refined.append(loc)
        else:
            refined.append(BeamAction(ti, ri, s, "gnn_multi_bs"))
    return refined


def mean_snr_db(actions: list[BeamAction]) -> float:
    lin = float(sum(max(a.snr_linear, 1e-18) for a in actions) / max(len(actions), 1))
    return 10.0 * np.log10(lin)


def run_multi_bs_episode(
    Hs_seq: list[list[np.ndarray]],
    tx_cb: np.ndarray,
    rx_cb: np.ndarray,
    mode: str,
) -> dict[str, float]:
    n_sw = 0
    pred = []
    prev: list[BeamAction] | None = None
    for Hs in Hs_seq:
        if mode == "independent_multi_bs":
            acts = independent_multi_bs(Hs, tx_cb, rx_cb)
        elif mode == "gnn_no_message":
            acts = gnn_multi_bs(Hs, tx_cb, rx_cb, message_passing=False)
        else:
            acts = gnn_multi_bs(Hs, tx_cb, rx_cb, message_passing=True)
        pred.extend(a.snr_linear for a in acts)
        if prev is not None:
            for a, b in zip(prev, acts):
                if a.tx_idx != b.tx_idx or a.rx_idx != b.rx_idx:
                    n_sw += 1
        prev = acts
    mean_lin = float(sum(pred) / max(len(pred), 1))
    return {
        "mean_snr_linear": mean_lin,
        "mean_snr_db": float(10.0 * np.log10(max(mean_lin, 1e-18))),
        "n_beam_switches": float(n_sw),
        "n_bs": float(len(Hs_seq[0]) if Hs_seq else 0),
    }
