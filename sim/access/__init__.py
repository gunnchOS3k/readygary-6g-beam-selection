"""Sub-6 access: cell/sector, Type-I CSI ranking, handover — not FR2 beam sweep."""
from __future__ import annotations

from typing import Any

import numpy as np

from sim.access.radio_decision import RadioDecision, RadioDecisionContext
from sim.experiments.digital_programme import beam_snr, dft_codebook


def type1_codebook(n_ports: int, n_beams: int) -> np.ndarray:
    """DFT Type-I single-panel codebook stand-in (TS 38.214 structure, digital)."""
    return dft_codebook(n_beams, n_ports)


def rank_csi(H: np.ndarray, codebook: np.ndarray) -> dict[str, Any]:
    """Rank PMI by |w^H H^H H w| proxy. Not analog FR2 beam training."""
    gram = H.conj().T @ H
    scores = []
    for i, w in enumerate(codebook):
        val = np.abs(w.conj() @ gram @ w)
        scores.append((i, float(val)))
    scores.sort(key=lambda x: x[1], reverse=True)
    pmi = scores[0][0]
    ri = 1 if codebook.shape[0] <= 4 else 2
    return {"pmi": pmi, "ri": ri, "csi_score": scores[0][1], "ranked": scores[:4]}


def select_cell(rsrp_dbm: list[float], hysteresis_db: float = 3.0, serving: int = 0) -> dict[str, Any]:
    best = int(np.argmax(rsrp_dbm))
    if rsrp_dbm[best] > rsrp_dbm[serving] + hysteresis_db:
        return {"cell": best, "handover": best != serving, "event": "A3"}
    return {"cell": serving, "handover": False, "event": "hold"}


def decide_sub6(ctx: RadioDecisionContext, H: np.ndarray | None = None) -> RadioDecision:
    m = ctx.measurements
    rsrp = list(m.get("rsrp_dbm") or [-90.0, -95.0, -102.0])
    cell = select_cell(rsrp, hysteresis_db=float(m.get("ho_hysteresis_db", 3.0)), serving=int(m.get("serving_cell", 0)))
    n_ports = int(m.get("n_ports", 4))
    cb = type1_codebook(n_ports, int(m.get("n_pmi", 8)))
    if H is None:
        rng = np.random.default_rng(ctx.seed)
        H = (rng.normal(size=(n_ports, n_ports)) + 1j * rng.normal(size=(n_ports, n_ports))) * 0.25
    csi = rank_csi(H, cb)
    sinr = float(m.get("sinr_sub6_db", 12.0))
    congestion = float(m.get("congestion", 0.0))
    rate = float(m.get("rate_sub6_mbps", 40.0))
    min_rate = float(m.get("min_useful_mbps", 0.0))
    useful = sinr >= float(m.get("min_sinr_db", 0.0)) and congestion < 0.95
    if min_rate > 0:
        useful = useful and rate >= min_rate
    if m.get("compute_placement") == "unavailable" and str(m.get("needs_offload", False)) == "True":
        useful = False
    costs = {
        "ho_delay_ms": 40.0 if cell["handover"] else 0.0,
        "signaling": 1.0 if cell["handover"] else 0.1,
        "outage": 0.0 if useful else 1.0,
        "beam_training": 0.0,
        "energy": 0.4 + 0.3 * congestion,
        "compute": 0.2,
        "interruption_ms": 40.0 if cell["handover"] else 0.0,
        "uncertainty": 0.2 + 0.2 * congestion,
        "csi_score": float(csi["csi_score"]),
    }
    return RadioDecision(
        action="handover_cell" if cell["handover"] else "stay_sub6",
        serving_family="SUB6",
        serving_band_id=str(m.get("band_id", "n77")),
        spatial={"mode": "type1_csi", "pmi": csi["pmi"], "ri": csi["ri"], "cell": cell["cell"]},
        fidelity=str(m.get("fidelity", "full")),
        compute_placement=str(m.get("compute_placement", "local")),
        costs=costs,
        rationale="Sub-6 cell/CSI ranking; not FR2 analog beam management",
        min_useful_service=useful,
        extras={"handover_event": cell["event"], "rsrp_dbm": rsrp},
    )


def decide_fr2(ctx: RadioDecisionContext, H: np.ndarray | None = None) -> RadioDecision:
    m = ctx.measurements
    n_tx = int(m.get("n_tx", 8))
    cb = dft_codebook(n_tx, n_tx)
    if H is None:
        rng = np.random.default_rng(ctx.seed + 1)
        H = rng.normal(size=(n_tx, n_tx)) + 1j * rng.normal(size=(n_tx, n_tx))
    best_t, best_r, best_s = 0, 0, -1.0
    for t in range(n_tx):
        for r in range(n_tx):
            s = beam_snr(H, cb, cb, t, r)
            if s > best_s:
                best_t, best_r, best_s = t, r, s
    blocked = bool(m.get("fr2_blockage", False))
    sinr = float(m.get("sinr_fr2_db", 10.0 * np.log10(max(best_s, 1e-18))))
    if blocked:
        sinr -= float(m.get("blockage_db", 18.0))
    useful = (not blocked) and sinr >= float(m.get("min_sinr_db", 3.0))
    costs = {
        "ho_delay_ms": 0.0,
        "signaling": 0.4,
        "outage": 1.0 if blocked else 0.0,
        "beam_training": 2.5,
        "energy": 0.9,
        "compute": 0.5,
        "interruption_ms": 8.0 if blocked else 1.0,
        "uncertainty": 0.6 if blocked else 0.25,
        "snr_linear": float(best_s),
    }
    return RadioDecision(
        action="stay_fr2" if not blocked else "fr2_blocked",
        serving_family="FR2",
        serving_band_id=str(m.get("fr2_band_id", "n257")),
        spatial={"mode": "analog_dft_beam", "tx_idx": best_t, "rx_idx": best_r},
        fidelity=str(m.get("fidelity", "full")),
        compute_placement=str(m.get("compute_placement", "edge")),
        costs=costs,
        rationale="FR2 analog DFT beam pair; not Sub-6 Type-I CSI",
        min_useful_service=useful,
        extras={"blockage": blocked, "sinr_db": sinr},
    )
