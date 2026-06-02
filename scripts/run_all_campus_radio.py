#!/usr/bin/env python3
from pathlib import Path
import yaml

cfg = Path(__file__).resolve().parents[1] / "configs" / "campus_radio_profiles"
out = Path("results/campus_radio")
out.mkdir(parents=True, exist_ok=True)
for p in sorted(cfg.glob("*.yaml")):
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    sid = data["site_id"]
    (out / f"{sid}_radio_profile_report.md").write_text(
        f"# Radio profile — {sid}\n\nMobility: {data['mobility_case']}\n\nEvidence: {data['evidence_status']}\n", encoding="utf-8"
    )
print("Wrote campus radio reports")
