"""Signed oracle gap on the 28 GHz synthetic beam programme.

A negative db_loss_vs_oracle means the reported policy mean linear SNR is
above the exhaustive-oracle mean. That signed gap is a SYNTHETIC_SIM
diagnostic at 28e9 Hz. It is not a measured improvement and not a physical
FR2 result.
"""
from __future__ import annotations

import numpy as np

import sim.experiments.digital_programme as dp


def test_negative_oracle_gap_is_not_clamped_to_zero(monkeypatch):
    assert dp.__doc__ is not None
    assert "28e9" in dp.__doc__
    assert "SYNTHETIC_SIM" in dp.__doc__

    def tiny_oracle(H, tx_cb, rx_cb):
        return 0, 0, 1.0

    def policy_above_oracle(slot, prev, tx_cb, rx_cb, proto, ablation):
        return dp.BeamAction(0, 0, 100.0, "probe_above_oracle_mean")

    monkeypatch.setattr(dp, "exhaustive", tiny_oracle)
    monkeypatch.setitem(dp.POLICIES, "no_adaptation", policy_above_oracle)

    slot = dp.ChannelSlot(
        H=np.ones((2, 2), dtype=np.complex128),
        aoa=0.1,
        aod=0.2,
        family="in_distribution",
    )
    tx = np.eye(2, dtype=np.complex128)
    rx = np.eye(2, dtype=np.complex128)
    row = dp.run_policy_on_episode(
        [slot],
        "no_adaptation",
        {"costs": {"beam_switch_penalty_db": 0.25}},
        tx,
        rx,
        "full",
    )
    signed = dp.snr_db(1.0) - dp.snr_db(100.0)
    assert signed < 0
    assert row["db_loss_vs_oracle"] == signed
    assert row["db_loss_vs_oracle"] < 0
