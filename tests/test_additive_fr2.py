"""Channel / GNN / adaptive / deploy tests. Numpy only."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from deploy.onnx_export import main as export_main
from deploy.server import health_payload, infer_payload
from deploy.tensorrt_compile import probe as trt_probe
from deploy.tiny_beam_scorer import seeded_scorer
from sim.channels import availability_report, get_backend
from sim.experiments.digital_programme import dft_codebook, load_protocol
from sim.models.gnn_multi_bs import run_multi_bs_episode
from sim.policies.adaptive_tracking import run_tracker_episode

ROOT = Path(__file__).resolve().parents[1]
ADD = ROOT / "paper" / "artifacts" / "experiment_protocol_additive.yaml"


def test_additive_protocol_fr2():
    proto = load_protocol(ADD)
    assert proto["carrier"]["band"] == "FR2"
    assert proto["carrier"]["frequency_hz"] == 28_000_000_000
    assert proto["sub_ms_inference_proven"] is False
    assert proto["sub_ms_inference_target"] is True


def test_open_backends_draw():
    proto = load_protocol(ADD)
    rng = np.random.default_rng(1)
    for name in ("synthetic", "tdl_a", "tdl_c", "cdl_a"):
        draw = get_backend(name).draw(rng, proto, "in_distribution")
        assert draw.H.shape == (8, 8)
        assert draw.evidence_class == "SYNTHETIC_SIM"
        assert draw.provenance.get("band") == "FR2" or draw.backend in {"synthetic", "tdl_a", "tdl_c", "cdl_a"}


def test_optional_backends_do_not_crash():
    report = availability_report()
    assert report["sionna_rt"]["available"] in (True, False)
    assert report["aodt"]["available"] in (True, False)
    proto = load_protocol(ADD)
    rng = np.random.default_rng(2)
    sionna = get_backend("sionna_rt").draw(rng, proto, "in_distribution")
    assert sionna.H.shape == (8, 8)


def test_gnn_ablation_runs():
    rng = np.random.default_rng(0)
    tx = dft_codebook(8, 8)
    rx = dft_codebook(8, 8)
    Hs_seq = [[rng.normal(size=(8, 8)) + 1j * rng.normal(size=(8, 8)) for _ in range(3)] for _ in range(2)]
    a = run_multi_bs_episode(Hs_seq, tx, rx, "independent_multi_bs")
    b = run_multi_bs_episode(Hs_seq, tx, rx, "gnn_multi_bs")
    c = run_multi_bs_episode(Hs_seq, tx, rx, "gnn_no_message")
    assert a["n_bs"] == 3
    assert np.isfinite(b["mean_snr_db"])
    assert np.isfinite(c["mean_snr_db"])


def test_adaptive_trackers_and_negative_ok():
    from sim.experiments.digital_programme import ChannelSlot

    proto = load_protocol(ADD)
    rng = np.random.default_rng(3)
    be = get_backend("tdl_a")
    slots = [
        ChannelSlot(H=d.H, aoa=d.aoa, aod=d.aod, family="in_distribution")
        for d in [be.draw(rng, proto, "in_distribution") for _ in range(4)]
    ]
    tx = dft_codebook(8, 8)
    rx = dft_codebook(8, 8)
    rows = {}
    for name in ("adaptive_static", "adaptive_heuristic", "adaptive_opt", "adaptive_bandit", "adaptive_constrained_rl"):
        rows[name] = run_tracker_episode(slots, name, tx, rx, rng=rng, probe_budget=1)
        assert np.isfinite(rows[name]["mean_snr_db"])
    # Negative result allowed: static may beat bandit under probe_budget=1.
    assert "mean_snr_db" in rows["adaptive_bandit"]


def test_deploy_npz_and_health():
    assert export_main() == 0
    npz = ROOT / "deploy" / "artifacts" / "tiny_beam_scorer.npz"
    assert npz.is_file()
    h = health_payload()
    assert h["status"] == "ok"
    assert h["band"] == "FR2"
    assert h["sub_ms_inference_proven"] is False
    trt = trt_probe()
    assert trt["sub_ms_inference_proven"] is False
    H = np.eye(8)
    out = infer_payload({"H_real": H.real.tolist(), "H_imag": H.imag.tolist()})
    assert 0 <= out["tx_beam"] < 8
    assert out["timing_ms"]["full"] >= 0.0


def test_scorer_batch1():
    s = seeded_scorer(7)
    H = np.ones((8, 8), dtype=np.complex128)
    assert isinstance(s.infer(H), int)


def test_timing_stages_exist(tmp_path, monkeypatch):
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "run_timing_harness", ROOT / "scripts" / "run_timing_harness.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    stages = mod.stage_times(n_warmup=1, n_trials=4, seed=0)
    for key in ("pre", "model", "post", "full"):
        assert "p50_ms" in stages[key]
        assert "p95_ms" in stages[key]
        assert "p99_ms" in stages[key]
