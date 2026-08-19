"""Sub-6 / dual-band / firewall / GNN-RL / deploy tests. Numpy only."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from sim.access import decide_fr2, decide_sub6
from sim.access.radio_decision import RadioDecisionContext
from sim.bands import load_all_profiles, primary_sub6
from sim.channels import availability_report, get_backend
from sim.channels.sub6 import doppler_hz, uma_nlos_pathloss_db
from sim.devices import available_families, device
from sim.dualband.controller import POLICIES, decide
from sim.experiments.digital_programme import dft_codebook, load_protocol
from sim.experiments.sub6_programme import load_sub6_protocol
from sim.experiments.dualband_programme import load_dual_protocol
from sim.models.gnn_trainable import classify_existing_gnn, train_on_oracle
from sim.policies.sequential_band import classify_rl

ROOT = Path(__file__).resolve().parents[1]


def test_band_profiles_firewall():
    allp = load_all_profiles()
    p = primary_sub6()
    assert p.band_id == "n77"
    assert p.fc_hz == 3_750_000_000
    assert p.fc_hz < 6_000_000_000
    assert allp["n257_28ghz"].family == "FR2"
    assert allp["n257_28ghz"].fc_hz == 28_000_000_000
    assert allp["n96_unlicensed_fr1"].family == "FR1_NOT_BELOW_6GHZ"
    assert allp["n96_unlicensed_fr1"].below_6ghz is False
    assert allp["n41_us_2500"].below_6ghz is True
    assert allp["n71_us_600"].below_6ghz is True


def test_sub6_protocol_not_28ghz():
    proto = load_sub6_protocol()
    assert proto["carrier"]["frequency_hz"] == 3_750_000_000
    assert proto["carrier"]["family"] == "SUB6"
    assert proto["carrier"]["below_6ghz"] is True


def test_fr2_protocol_regression():
    proto = load_protocol(ROOT / "paper" / "artifacts" / "experiment_protocol.yaml")
    assert proto["carrier"]["band"] == "FR2"
    assert proto["carrier"]["frequency_hz"] == 28_000_000_000


def test_sub6_channel_refuses_28ghz():
    be = get_backend("sub6_tdl_a")
    rng = np.random.default_rng(0)
    proto = {
        "carrier": {"frequency_hz": 28_000_000_000, "band": "FR2", "family": "FR2"},
        "channel": {"num_tx_ant": 4, "num_rx_ant": 4},
    }
    try:
        be.draw(rng, proto, "in_distribution")
        raise AssertionError("28 GHz must be refused by Sub-6 backend")
    except ValueError:
        pass


def test_sub6_channel_distinct_from_fr2_pathloss():
    pl_sub6 = uma_nlos_pathloss_db(35.0, 3.75e9)
    pl_fr2 = uma_nlos_pathloss_db(35.0, 28e9)
    assert pl_fr2 > pl_sub6 + 10.0
    assert doppler_hz(22.0, 28e9) > 5.0 * doppler_hz(22.0, 3.75e9)
    proto = load_sub6_protocol()
    rng = np.random.default_rng(1)
    d1 = get_backend("sub6_tdl_a").draw(rng, proto, "in_distribution")
    assert d1.H.shape == (4, 4)
    assert d1.provenance["carrier_hz"] == 3_750_000_000
    assert d1.provenance["below_6ghz"] is True
    d2 = get_backend("sub6_tdl_a").draw(np.random.default_rng(1), proto, "congestion")
    assert d2.provenance["load"] >= d1.provenance["load"]


def test_fr2_open_backends_still_draw():
    proto = load_protocol(ROOT / "paper" / "artifacts" / "experiment_protocol_additive.yaml")
    rng = np.random.default_rng(1)
    for name in ("synthetic", "tdl_a", "tdl_c", "cdl_a"):
        draw = get_backend(name).draw(rng, proto, "in_distribution")
        assert draw.H.shape == (8, 8)
        assert int(draw.provenance.get("carrier_hz", 28e9)) == 28_000_000_000


def test_radio_decision_api_not_identical():
    ctx = RadioDecisionContext(
        device_class="student_14_5",
        workload="lecture_video",
        available_families=["SUB6", "FR2"],
        measurements={"sinr_sub6_db": 10.0, "sinr_fr2_db": 12.0, "fr2_blockage": False},
        seed=0,
    )
    a = decide_sub6(ctx)
    b = decide_fr2(ctx)
    assert a.spatial["mode"] == "type1_csi"
    assert b.spatial["mode"] == "analog_dft_beam"
    assert a.serving_family == "SUB6"
    assert b.serving_family == "FR2"


def test_dualband_policies_and_switching():
    ctx = RadioDecisionContext(
        device_class="student_14_5",
        workload="lecture_video",
        available_families=["SUB6", "FR2"],
        measurements={
            "sinr_sub6_db": 4.0,
            "sinr_fr2_db": 16.0,
            "fr2_blockage": False,
            "congestion": 0.9,
            "rate_sub6_mbps": 1.0,
            "rate_fr2_mbps": 400.0,
            "min_useful_mbps": 2.0,
            "preferred_family": "SUB6",
        },
        seed=2,
    )
    seen = set()
    prev = None
    for name in POLICIES:
        ctx.previous = prev
        dec = decide(name, ctx)
        seen.add(dec.serving_family)
        prev = dec
        assert dec.evidence_class == "SYNTHETIC_SIM"
        assert "ho_delay_ms" in dec.costs
    blocked = RadioDecisionContext(
        device_class="student_14_5",
        workload="lecture_video",
        available_families=["SUB6", "FR2"],
        measurements={"fr2_blockage": True, "sinr_fr2_db": -10.0, "sinr_sub6_db": 11.0, "rate_sub6_mbps": 20.0, "min_useful_mbps": 2.0},
        previous=decide("FR2_ONLY", ctx),
        seed=3,
    )
    sw = decide("SERVICE_AWARE_POLICY", blocked)
    assert sw.serving_family == "SUB6"
    assert sw.costs.get("switched") == 1.0


def test_device_classes_no_fabricated_rf():
    assert device("student_14_5")["wwan"] == "RM520N-GL"
    assert device("student_14_5")["rf_measured"] is False
    assert device("edge_io_rings")["sub6_capable"] is False
    assert "SUB6" in available_families("ds_xl_coder")
    assert available_families("edge_io_rings") == []


def test_gnn_rl_honest_classes():
    g = classify_existing_gnn()
    assert g["sim.models.gnn_multi_bs"] == "HEURISTIC_MESSAGE_PASSING"
    assert g["sim.models.gnn_trainable"] == "TRAINED_GRAPH_MODEL"
    r = classify_rl()
    assert r["adaptive_constrained_rl"] == "TABULAR_Q"
    assert r["sequential_band_policy"] == "REINFORCE_SEQUENTIAL"
    rng = np.random.default_rng(0)
    tx = dft_codebook(4, 4)
    Hs = [[rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4)) for _ in range(2)]]
    model = train_on_oracle(Hs, tx, tx, steps=2)
    assert model.predict(Hs[0])


def test_open_optional_backends_fail_closed():
    report = availability_report()
    assert "sub6_tdl_a" in report
    proto = load_sub6_protocol()
    rng = np.random.default_rng(4)
    s = get_backend("sionna_rt").draw(rng, proto, "in_distribution")
    assert s.H.shape[0] >= 2
    a = get_backend("aodt").draw(rng, proto, "in_distribution")
    assert a.provenance.get("ota") is False


def test_dual_protocol_carriers():
    proto = load_dual_protocol()
    assert proto["carriers"]["sub6"]["frequency_hz"] == 3_750_000_000
    assert proto["carriers"]["fr2"]["frequency_hz"] == 28_000_000_000
    assert proto["carriers"]["fr2"]["never"] == "Sub-6"


def test_deploy_cross_band_metadata():
    from deploy.server import health_payload, metadata_payload

    h = health_payload()
    assert h["band"] == "FR2"
    assert h["sub6_primary"] == "n77_us_cband"
    assert h["sub_ms_inference_proven"] is False
    assert "SUB6" in h["families"]
    meta = metadata_payload()
    assert meta.get("sub_ms_inference_proven") is False or "tensorrt" in meta
