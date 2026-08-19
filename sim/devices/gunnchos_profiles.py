"""gunnchOS device + workload coupling. MODELED_TARGET_RANGE. Not DEVICE_MEASURED RF/power."""
from __future__ import annotations

from typing import Any

# Hardware truth from sibling gunnchos-hardware-industrial-design (BOM freeze).
# Do not invent modem bands. Rings have no cellular.

DEVICE_CLASSES: dict[str, dict[str, Any]] = {
    "student_14_5": {
        "product": "Student 14.5",
        "wwan": "RM520N-GL",
        "wwan_required_for_fleet": True,
        "sub6_capable": True,
        "fr2_capable": False,
        "fr2_path": "TARGET_future_M2_module_swap",
        "compute_placement_default": "local",
        "thermal_headroom": "desk_sustained",
        "measurement_class": "MODELED_TARGET_RANGE",
        "rf_measured": False,
        "power_measured": False,
    },
    "handheld_hybrid": {
        "product": "Handheld Hybrid",
        "wwan": "RM520N-GL_optional_thermal_gated",
        "wwan_required_for_fleet": False,
        "sub6_capable": True,
        "fr2_capable": False,
        "fr2_path": "TARGET_future_M2_module_swap",
        "compute_placement_default": "local",
        "thermal_headroom": "handheld_limited",
        "wifi_first": True,
        "measurement_class": "MODELED_TARGET_RANGE",
        "rf_measured": False,
        "power_measured": False,
    },
    "ds_xl_coder": {
        "product": "DS-XL Coder",
        "wwan": "RM520N-GL",
        "wwan_required_for_fleet": True,
        "sub6_capable": True,
        "fr2_capable": False,
        "fr2_path": "TARGET_future_M2_module_swap",
        "compute_placement_default": "local",
        "thermal_headroom": "desk_sustained",
        "measurement_class": "MODELED_TARGET_RANGE",
        "rf_measured": False,
        "power_measured": False,
    },
    "edge_io_rings": {
        "product": "Edge I/O Rings",
        "wwan": None,
        "wwan_required_for_fleet": False,
        "sub6_capable": False,
        "fr2_capable": False,
        "fr2_path": "N/A",
        "compute_placement_default": "companion_host",
        "thermal_headroom": "wearable",
        "wifi_first": True,
        "measurement_class": "MODELED_TARGET_RANGE",
        "rf_measured": False,
        "power_measured": False,
        "note": "No cellular on Rings; dual-band WWAN decisions are N/A",
    },
}

WORKLOADS: dict[str, dict[str, Any]] = {
    "lecture_video": {"min_useful_mbps": 2.0, "delay_budget_ms": 400.0, "loss_tolerance": "medium"},
    "interactive_tutor": {"min_useful_mbps": 0.2, "delay_budget_ms": 150.0, "loss_tolerance": "low"},
    "cloud_ide": {"min_useful_mbps": 1.0, "delay_budget_ms": 250.0, "loss_tolerance": "low"},
    "background_sync": {"min_useful_mbps": 0.05, "delay_budget_ms": 5000.0, "loss_tolerance": "high"},
    "emergency_text": {"min_useful_mbps": 0.01, "delay_budget_ms": 2000.0, "loss_tolerance": "high"},
}


def device(device_id: str) -> dict[str, Any]:
    if device_id not in DEVICE_CLASSES:
        raise KeyError(device_id)
    return dict(DEVICE_CLASSES[device_id])


def workload(name: str) -> dict[str, Any]:
    if name not in WORKLOADS:
        raise KeyError(name)
    return dict(WORKLOADS[name])


def available_families(device_id: str, *, fr2_research_path: bool = True) -> list[str]:
    d = device(device_id)
    fam = []
    if d.get("sub6_capable"):
        fam.append("SUB6")
    if fr2_research_path and device_id != "edge_io_rings":
        # FR2 is a research/future-module path, not the BOM modem.
        fam.append("FR2")
    return fam


def continuity_context_defaults(device_id: str, workload_name: str) -> dict[str, Any]:
    d = device(device_id)
    w = workload(workload_name)
    return {
        "device_class": device_id,
        "workload": workload_name,
        "available_families": available_families(device_id),
        "min_useful_mbps": w["min_useful_mbps"],
        "delay_budget_ms": w["delay_budget_ms"],
        "compute_placement": d["compute_placement_default"],
        "measurement_class": d["measurement_class"],
        "rf_measured": False,
        "power_measured": False,
        "wwan": d.get("wwan"),
    }
