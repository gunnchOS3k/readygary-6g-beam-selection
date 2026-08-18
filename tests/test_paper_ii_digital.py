"""Paper II FR2 beam digital programme tests."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from sim.experiments.digital_programme import (
    PROTOCOL_RELPATH,
    aoa_to_beam_index,
    dft_codebook,
    exhaustive,
    generate_slot,
    load_protocol,
    mean_ci,
    run_family,
)


ROOT = Path(__file__).resolve().parents[1]


def test_protocol_fr2_not_sub6():
    proto = load_protocol(ROOT / PROTOCOL_RELPATH)
    assert proto["frozen"] is True
    assert proto["carrier"]["frequency_hz"] == 28000000000
    assert proto["carrier"]["band"] == "FR2"
    assert proto["latency_class"] == "HOST_PROCESS_TIMING"
    assert proto["sub_ms_inference_proven"] is False
    assert proto["evidence_class"] == "SYNTHETIC_SIM"


def test_oracle_beats_or_ties_fixed_beam():
    proto = load_protocol(ROOT / PROTOCOL_RELPATH)
    proto["split"] = {
        **proto["split"],
        "train_seeds": [0],
        "n_episodes_per_seed": 2,
        "n_slots_per_episode": 3,
    }
    out = run_family(
        proto,
        family="in_distribution",
        seeds=[0],
        policies=["no_adaptation", "information_equivalent", "twin_informed", "exhaustive_oracle"],
    )
    assert out["latency_class"] == "HOST_PROCESS_TIMING"
    assert out["band"] == "FR2"
    na = out["policies"]["no_adaptation"]["mean_snr_linear"]["mean"]
    ora = out["policies"]["exhaustive_oracle"]["mean_snr_linear"]["mean"]
    assert ora + 1e-12 >= na


def test_aoa_index_in_range():
    cb = dft_codebook(8, 8)
    idx = aoa_to_beam_index(0.3, cb.shape[0])
    assert 0 <= idx < 8


def test_mean_ci():
    s = mean_ci([1.0, 2.0, 3.0, 4.0, 5.0])
    assert abs(s["mean"] - 3.0) < 1e-12
    assert s["ci_low"] < s["mean"] < s["ci_high"]


def test_generate_slot_is_fr2_family():
    proto = load_protocol(ROOT / PROTOCOL_RELPATH)
    rng = np.random.default_rng(1)
    slot = generate_slot(rng, proto, "in_distribution")
    assert slot.H.shape == (8, 8)
    tx = dft_codebook(8, 8)
    rx = dft_codebook(8, 8)
    ti, ri, s = exhaustive(slot.H, tx, rx)
    assert s >= 0.0
    assert 0 <= ti < 8 and 0 <= ri < 8
