"""Common radio decision API. Sub-6 physics ≠ FR2 analog beam management."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class RadioDecisionContext:
    device_class: str
    workload: str
    available_families: list[str]
    measurements: dict[str, Any]
    twin_hint: dict[str, Any] | None = None
    previous: "RadioDecision | None" = None
    seed: int = 0
    profile_sub6: str = "n77_us_cband"
    profile_fr2: str = "n257_28ghz"


@dataclass
class RadioDecision:
    action: str
    serving_family: str
    serving_band_id: str
    spatial: dict[str, Any]
    fidelity: str
    compute_placement: str
    costs: dict[str, float]
    rationale: str
    evidence_class: str = "SYNTHETIC_SIM"
    min_useful_service: bool = False
    extras: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "serving_family": self.serving_family,
            "serving_band_id": self.serving_band_id,
            "spatial": self.spatial,
            "fidelity": self.fidelity,
            "compute_placement": self.compute_placement,
            "costs": self.costs,
            "rationale": self.rationale,
            "evidence_class": self.evidence_class,
            "min_useful_service": self.min_useful_service,
            "extras": self.extras,
        }


class RadioPolicy(Protocol):
    name: str

    def decide(self, ctx: RadioDecisionContext) -> RadioDecision:
        ...
