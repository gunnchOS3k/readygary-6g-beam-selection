"""Dual-band continuity controller.

Primary outcome: min-useful service, not peak throughput.
SYNTHETIC_SIM. Switch costs are modeled, not measured RF.
"""
from __future__ import annotations

from typing import Any, Callable

import numpy as np

from sim.access import decide_fr2, decide_sub6
from sim.access.radio_decision import RadioDecision, RadioDecisionContext

POLICIES = (
    "SUB6_ONLY",
    "FR2_ONLY",
    "STATIC_PREFERRED",
    "SIGNAL_POLICY",
    "SERVICE_AWARE_POLICY",
    "DIGITAL_TWIN_POLICY",
    "OPTIMIZATION_REFERENCE",
    "LEARNED_POLICY",
)


def _band_ok(family: str, ctx: RadioDecisionContext) -> bool:
    return family in ctx.available_families


def _switch_costs(prev: RadioDecision | None, nxt: RadioDecision) -> dict[str, float]:
    switched = prev is not None and prev.serving_family != nxt.serving_family
    extra = {
        "ho_delay_ms": 60.0 if switched else 0.0,
        "signaling": 2.0 if switched else 0.0,
        "interruption_ms": 80.0 if switched else 0.0,
        "uncertainty": 0.35 if switched else 0.05,
    }
    merged = dict(nxt.costs)
    for k, v in extra.items():
        merged[k] = float(merged.get(k, 0.0)) + v
    merged["switched"] = 1.0 if switched else 0.0
    return merged


def _with_costs(ctx: RadioDecisionContext, dec: RadioDecision) -> RadioDecision:
    dec.costs = _switch_costs(ctx.previous, dec)
    if dec.costs.get("switched"):
        if dec.action.startswith("stay_"):
            dec.action = f"switch_to_{dec.serving_family.lower()}"
    return dec


def policy_sub6_only(ctx: RadioDecisionContext) -> RadioDecision:
    dec = decide_sub6(ctx)
    return _with_costs(ctx, dec)


def policy_fr2_only(ctx: RadioDecisionContext) -> RadioDecision:
    dec = decide_fr2(ctx)
    return _with_costs(ctx, dec)


def policy_static_preferred(ctx: RadioDecisionContext) -> RadioDecision:
    pref = str(ctx.measurements.get("preferred_family", "SUB6"))
    if pref == "FR2" and _band_ok("FR2", ctx):
        return _with_costs(ctx, decide_fr2(ctx))
    return _with_costs(ctx, decide_sub6(ctx))


def policy_signal(ctx: RadioDecisionContext) -> RadioDecision:
    m = ctx.measurements
    sub6 = float(m.get("sinr_sub6_db", 8.0))
    fr2 = float(m.get("sinr_fr2_db", -5.0))
    blocked = bool(m.get("fr2_blockage", False))
    congested = float(m.get("congestion", 0.0)) > 0.75
    if blocked or fr2 < 0.0 or (congested is False and sub6 + 3.0 < fr2 and _band_ok("FR2", ctx)):
        if _band_ok("FR2", ctx) and not blocked and fr2 >= sub6 + 3.0:
            return _with_costs(ctx, decide_fr2(ctx))
    if congested and _band_ok("FR2", ctx) and not blocked:
        return _with_costs(ctx, decide_fr2(ctx))
    return _with_costs(ctx, decide_sub6(ctx))


def policy_service_aware(ctx: RadioDecisionContext) -> RadioDecision:
    m = ctx.measurements
    workload = ctx.workload
    min_rate = float(m.get("min_useful_mbps", 2.0))
    sub6_rate = float(m.get("rate_sub6_mbps", 40.0)) * (1.0 - float(m.get("congestion", 0.0)))
    fr2_rate = 0.0 if m.get("fr2_blockage") else float(m.get("rate_fr2_mbps", 800.0))
    delay_budget_ms = float(m.get("delay_budget_ms", 150.0 if workload == "interactive_tutor" else 400.0))
    # Prefer the band that meets min-useful with lower interruption, not peak rate.
    sub6_ok = sub6_rate >= min_rate
    fr2_ok = fr2_rate >= min_rate and _band_ok("FR2", ctx)
    if sub6_ok:
        dec = decide_sub6(ctx)
        dec.min_useful_service = True
        dec.extras["offered_mbps"] = sub6_rate
        dec.extras["delay_budget_ms"] = delay_budget_ms
        return _with_costs(ctx, dec)
    if fr2_ok:
        dec = decide_fr2(ctx)
        dec.min_useful_service = True
        dec.extras["offered_mbps"] = fr2_rate
        return _with_costs(ctx, dec)
    # Neither meets min-useful: stay Sub-6 coverage and degrade fidelity.
    dec = decide_sub6(ctx)
    dec.fidelity = "degraded"
    dec.min_useful_service = False
    dec.action = "degrade_fidelity"
    dec.rationale = "Neither band meets min-useful; degrade fidelity on Sub-6 coverage"
    return _with_costs(ctx, dec)


def policy_digital_twin(ctx: RadioDecisionContext) -> RadioDecision:
    hint = ctx.twin_hint or {}
    if hint.get("fr2_los") is True and not ctx.measurements.get("fr2_blockage") and _band_ok("FR2", ctx):
        dec = decide_fr2(ctx)
        dec.rationale = "Twin LOS hint selected FR2; twin ≠ OTA"
        return _with_costs(ctx, dec)
    if hint.get("indoor") or hint.get("predicted_blockage"):
        dec = decide_sub6(ctx)
        dec.rationale = "Twin indoor/blockage hint selected Sub-6; twin ≠ OTA"
        return _with_costs(ctx, dec)
    return policy_service_aware(ctx)


def policy_optimization_reference(ctx: RadioDecisionContext) -> RadioDecision:
    """Oracle among {Sub-6, FR2} using modeled min-useful then interruption, then energy."""
    a = decide_sub6(ctx)
    b = decide_fr2(ctx)
    cands = []
    if _band_ok("SUB6", ctx):
        cands.append(a)
    if _band_ok("FR2", ctx):
        cands.append(b)

    def key(d: RadioDecision) -> tuple:
        return (
            int(d.min_useful_service),
            -float(d.costs.get("interruption_ms", 0.0)),
            -float(d.costs.get("outage", 0.0)),
            -float(d.costs.get("energy", 0.0)),
        )

    best = max(cands, key=key)
    best.rationale = "Optimization reference over modeled min-useful/interruption/energy"
    return _with_costs(ctx, best)


def policy_learned(ctx: RadioDecisionContext, weights: np.ndarray | None = None) -> RadioDecision:
    """Linear sequential policy over [sub6_sinr, fr2_sinr, blockage, congestion, indoor]."""
    m = ctx.measurements
    x = np.array(
        [
            float(m.get("sinr_sub6_db", 0.0)),
            float(m.get("sinr_fr2_db", 0.0)),
            1.0 if m.get("fr2_blockage") else 0.0,
            float(m.get("congestion", 0.0)),
            1.0 if m.get("indoor") else 0.0,
        ],
        dtype=np.float64,
    )
    w = weights if weights is not None else np.array([0.6, 0.25, -1.4, -0.8, 0.7])
    score_sub6 = float(w @ np.array([x[0], 0.0, 0.0, -x[3], x[4]]))
    score_fr2 = float(w @ np.array([0.0, x[1], -2.0 * x[2], 0.2 * (1.0 - x[3]), -x[4]]))
    if score_fr2 > score_sub6 and _band_ok("FR2", ctx) and not m.get("fr2_blockage"):
        dec = decide_fr2(ctx)
    else:
        dec = decide_sub6(ctx)
    dec.extras["learned_scores"] = {"sub6": score_sub6, "fr2": score_fr2}
    dec.rationale = "Learned linear sequential policy (trained weights or default)"
    return _with_costs(ctx, dec)


DISPATCH: dict[str, Callable[[RadioDecisionContext], RadioDecision]] = {
    "SUB6_ONLY": policy_sub6_only,
    "FR2_ONLY": policy_fr2_only,
    "STATIC_PREFERRED": policy_static_preferred,
    "SIGNAL_POLICY": policy_signal,
    "SERVICE_AWARE_POLICY": policy_service_aware,
    "DIGITAL_TWIN_POLICY": policy_digital_twin,
    "OPTIMIZATION_REFERENCE": policy_optimization_reference,
    "LEARNED_POLICY": policy_learned,
}


def decide(policy: str, ctx: RadioDecisionContext) -> RadioDecision:
    if policy not in DISPATCH:
        raise KeyError(f"Unknown dual-band policy {policy}")
    return DISPATCH[policy](ctx)
