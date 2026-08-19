#!/usr/bin/env python3
"""Generate Paper II ReadyGary tables/figures from JSON. RESULT_PENDING if missing."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "paper" / "tables"
FIGS = ROOT / "paper" / "figures"
TABLES.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)
EXP = ROOT / "results" / "experiments"
HELD = EXP / "rq2_beam_selection_fr2_heldout.json"
TRAIN = EXP / "rq2_beam_selection_fr2_train.json"
SHIFT = EXP / "rq2_beam_selection_fr2_domain_shift.json"
ABL = EXP / "rq2_beam_selection_fr2_ablation.json"


def pending(path: Path, msg: str) -> None:
    path.write_text(f"\\textbf{{RESULT\\_PENDING.}} {msg}\\par\n", encoding="utf-8")
    print("RESULT_PENDING", path)


def fmt(x: object, nd: int = 4) -> str:
    if isinstance(x, float):
        if x != x:
            return "nan"
        return f"{x:.{nd}f}"
    return str(x)


def write_policy_table(src: Path, stem: str, caption: str) -> None:
    tex = TABLES / f"{stem}.tex"
    md = TABLES / f"{stem}.md"
    csv_path = TABLES / f"{stem}.csv"
    if not src.exists():
        pending(tex, f"Missing {src.name}.")
        md.write_text(f"**RESULT_PENDING.** Missing `{src}`.\n", encoding="utf-8")
        return
    data = json.loads(src.read_text(encoding="utf-8"))
    policies = data.get("policies") or {}
    effects = data.get("effect_sizes") or {}
    rows = []
    for name, block in policies.items():
        snr = block.get("mean_snr_db") or {}
        loss = block.get("db_loss_vs_oracle") or {}
        top1 = block.get("top1_match_oracle") or {}
        sw = block.get("n_beam_switches") or {}
        cpu = block.get("compute_time_ms") or {}
        d = (effects.get(name) or {}).get("cohens_d_vs_no_adaptation_snr_db", "")
        rows.append({
            "policy": name,
            "snr_db_mean": snr.get("mean"),
            "snr_db_ci_low": snr.get("ci_low"),
            "snr_db_ci_high": snr.get("ci_high"),
            "db_loss_vs_oracle": loss.get("mean"),
            "top1_match_oracle": top1.get("mean"),
            "n_beam_switches": sw.get("mean"),
            "compute_time_ms": cpu.get("mean"),
            "cohens_d_vs_no_adaptation": d,
        })
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["policy"])
        w.writeheader()
        w.writerows(rows)
    md_lines = [
        f"# {stem} (SYNTHETIC_SIM, HOST_PROCESS_TIMING, FR2 28 GHz)",
        "",
        f"Family `{data.get('family')}`; seeds `{data.get('seeds')}`. Not measured RF. Sub-ms unproven.",
        "",
        "| policy | SNR dB mean [95% CI] | dB loss vs oracle | top1 | switches | compute_ms | Cohen's d vs no_adaptation |",
        "|---|---|---|---|---|---|---|",
    ]
    tex_rows = []
    for r in rows:
        ci = f"{fmt(r['snr_db_mean'])} [{fmt(r['snr_db_ci_low'])}, {fmt(r['snr_db_ci_high'])}]"
        md_lines.append(
            f"| `{r['policy']}` | {ci} | {fmt(r['db_loss_vs_oracle'])} | {fmt(r['top1_match_oracle'])} | {fmt(r['n_beam_switches'])} | {fmt(r['compute_time_ms'])} | {fmt(r['cohens_d_vs_no_adaptation'])} |"
        )
        tex_rows.append(
            f"{r['policy'].replace('_', '\\_')} & {fmt(r['snr_db_mean'])} & {fmt(r['snr_db_ci_low'])} & {fmt(r['snr_db_ci_high'])} & {fmt(r['db_loss_vs_oracle'])} & {fmt(r['top1_match_oracle'])} & {fmt(r['n_beam_switches'])} & {fmt(r['compute_time_ms'])} & {fmt(r['cohens_d_vs_no_adaptation'])} \\\\"
        )
    md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    tex.write_text(
        "\\begin{table}[h]\\centering\n"
        f"\\caption{{{caption}}}\n"
        "\\begin{tabular}{lrrrrrrrr}\\toprule\n"
        "policy & SNR dB & CI low & CI high & dB loss & top1 & switches & compute ms & $d$ \\\\\n"
        f"\\midrule\n{chr(10).join(tex_rows)}\n\\bottomrule\\end{{tabular}}\n\\end{{table}}\n",
        encoding="utf-8",
    )
    print("wrote", tex)


def write_shift() -> None:
    tex = TABLES / "rq2_beam_domain_shift.tex"
    md = TABLES / "rq2_beam_domain_shift.md"
    csv_path = TABLES / "rq2_beam_domain_shift.csv"
    if not SHIFT.exists():
        pending(tex, "Missing domain-shift JSON.")
        md.write_text("**RESULT_PENDING.** Missing domain-shift JSON.\n", encoding="utf-8")
        return
    data = json.loads(SHIFT.read_text(encoding="utf-8"))
    rows = []
    for fam, block in data.items():
        for name, pol in (block.get("policies") or {}).items():
            snr = pol.get("mean_snr_db") or {}
            rows.append({"family": fam, "policy": name, "snr_db_mean": snr.get("mean"), "ci_low": snr.get("ci_low"), "ci_high": snr.get("ci_high")})
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["family", "policy", "snr_db_mean", "ci_low", "ci_high"])
        w.writeheader()
        w.writerows(rows)
    md_lines = ["# rq2_beam_domain_shift (SYNTHETIC_SIM, FR2)", "", "| family | policy | SNR dB mean [95% CI] |", "|---|---|---|"]
    tex_rows = []
    for r in rows:
        md_lines.append(f"| `{r['family']}` | `{r['policy']}` | {fmt(r['snr_db_mean'])} [{fmt(r['ci_low'])}, {fmt(r['ci_high'])}] |")
        tex_rows.append(
            f"{str(r['family']).replace('_', '\\_')} & {str(r['policy']).replace('_', '\\_')} & {fmt(r['snr_db_mean'])} & {fmt(r['ci_low'])} & {fmt(r['ci_high'])} \\\\"
        )
    md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    tex.write_text(
        "\\begin{table}[h]\\centering\n"
        "\\caption{FR2 TDL domain-shift SNR (SYNTHETIC\\_SIM; HOST\\_PROCESS\\_TIMING).}\n"
        "\\begin{tabular}{llrrr}\\toprule family & policy & SNR dB & CI low & CI high \\\\\\midrule\n"
        + "\n".join(tex_rows)
        + "\n\\bottomrule\\end{tabular}\\end{table}\n",
        encoding="utf-8",
    )
    print("wrote", tex)


def write_ablation() -> None:
    tex = TABLES / "rq2_beam_ablations.tex"
    md = TABLES / "rq2_beam_ablations.md"
    csv_path = TABLES / "rq2_beam_ablations.csv"
    if not ABL.exists():
        pending(tex, "Missing ablation JSON.")
        md.write_text("**RESULT_PENDING.** Missing ablation JSON.\n", encoding="utf-8")
        return
    data = json.loads(ABL.read_text(encoding="utf-8"))
    rows = []
    for name, block in data.items():
        for pol_name, pol in (block.get("policies") or {}).items():
            snr = pol.get("mean_snr_db") or {}
            rows.append({"ablation": name, "policy": pol_name, "snr_db_mean": snr.get("mean"), "ci_low": snr.get("ci_low"), "ci_high": snr.get("ci_high")})
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["ablation", "policy", "snr_db_mean", "ci_low", "ci_high"])
        w.writeheader()
        w.writerows(rows)
    md_lines = ["# rq2_beam_ablations (SYNTHETIC_SIM, FR2)", "", "| ablation | policy | SNR dB mean [95% CI] |", "|---|---|---|"]
    tex_rows = []
    for r in rows:
        md_lines.append(f"| `{r['ablation']}` | `{r['policy']}` | {fmt(r['snr_db_mean'])} [{fmt(r['ci_low'])}, {fmt(r['ci_high'])}] |")
        tex_rows.append(
            f"{str(r['ablation']).replace('_', '\\_')} & {str(r['policy']).replace('_', '\\_')} & {fmt(r['snr_db_mean'])} & {fmt(r['ci_low'])} & {fmt(r['ci_high'])} \\\\"
        )
    md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    tex.write_text(
        "\\begin{table}[h]\\centering\n"
        "\\caption{ReadyGary ablations (SYNTHETIC\\_SIM; FR2 TDL; HOST\\_PROCESS\\_TIMING).}\n"
        "\\begin{tabular}{llrrr}\\toprule ablation & policy & SNR dB & CI low & CI high \\\\\\midrule\n"
        + "\n".join(tex_rows)
        + "\n\\bottomrule\\end{tabular}\\end{table}\n",
        encoding="utf-8",
    )
    print("wrote", tex)


def write_figures() -> None:
    banner = FIGS / "README.md"
    png = FIGS / "rq2_heldout_snr.png"
    if not HELD.exists():
        banner.write_text("**RESULT_PENDING.** Held-out JSON missing; no figure generated.\n", encoding="utf-8")
        print("RESULT_PENDING figure")
        return
    data = json.loads(HELD.read_text(encoding="utf-8"))
    names, means, lows, highs = [], [], [], []
    for name, block in (data.get("policies") or {}).items():
        u = block.get("mean_snr_db") or {}
        if u.get("mean") is None:
            continue
        names.append(name)
        means.append(float(u["mean"]))
        lows.append(float(u.get("ci_low", u["mean"])))
        highs.append(float(u.get("ci_high", u["mean"])))
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        banner.write_text("**RESULT_PENDING.** matplotlib not importable.\n", encoding="utf-8")
        print("RESULT_PENDING matplotlib")
        return
    yerr = [[m - lo for m, lo in zip(means, lows)], [hi - m for m, hi in zip(means, highs)]]
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.bar(range(len(names)), means, yerr=yerr, capsize=3, color="#F58518")
    ax.set_xticks(range(len(names)), names, rotation=35, ha="right")
    ax.set_ylabel("mean SNR (dB)")
    ax.set_title("Held-out FR2 TDL SNR (SYNTHETIC_SIM; HOST_PROCESS_TIMING; 95% t CI)")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(png, dpi=150)
    plt.close(fig)
    banner.write_text(
        "Figures generated from `results/experiments/*.json`.\n\n"
        f"- `{png.name}`: held-out SNR means with 95% t CIs. 28 GHz FR2. Not measured RF.\n"
        "- `rq2_sub6_pathloss.png`: digital UMa-NLOS path loss at 35 m for n71/n41/n77 vs n257. Not OTA.\n",
        encoding="utf-8",
    )
    print("wrote", png)


def _ci_cell(block: dict, key: str) -> str:
    u = block.get(key) or {}
    if u.get("mean") is None:
        return "nan"
    return f"{fmt(u.get('mean'))} [{fmt(u.get('ci_low'))}, {fmt(u.get('ci_high'))}]"


def write_additive() -> None:
    src = EXP / "rq2_beam_selection_fr2_additive_heldout.json"
    if not src.exists():
        src = EXP / "rq2_beam_selection_fr2_additive_train.json"
    md = TABLES / "rq2_additive.md"
    tex = TABLES / "rq2_additive.tex"
    csv_path = TABLES / "rq2_additive.csv"
    if not src.exists():
        pending(tex, "Missing additive JSON.")
        md.write_text("**RESULT_PENDING.** Missing additive JSON.\n", encoding="utf-8")
        return
    data = json.loads(src.read_text(encoding="utf-8"))
    rows = []
    for name, block in (data.get("gnn_multi_bs") or {}).items():
        rows.append({"arm": "gnn", "name": name, "snr_db": (block.get("mean_snr_db") or {}).get("mean")})
    for name, block in (data.get("adaptive_tracking") or {}).items():
        rows.append({"arm": "adaptive", "name": name, "snr_db": (block.get("mean_snr_db") or {}).get("mean")})
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["arm", "name", "snr_db"])
        w.writeheader()
        w.writerows(rows)
    lines = [
        "# Additive FR2 arms (SYNTHETIC_SIM, HOST_PROCESS_TIMING, 28 GHz FR2, never Sub-6)",
        "",
        f"Source `{src.name}`. Twin/sim ≠ OTA. Sub-ms TARGET, not proven.",
        "",
        "## Channel backends",
        "",
        "| backend | available | evidence | oracle SNR linear mean |",
        "|---|---|---|---|",
    ]
    for name, block in (data.get("channel_oracle") or {}).items():
        ora = block.get("oracle_mean_snr_linear") or {}
        lines.append(
            f"| `{name}` | {block.get('available')} | {block.get('evidence_class')} | {fmt(ora.get('mean'))} |"
        )
    lines += ["", "## GNN multi-BS", "", "| mode | SNR dB mean [95% CI] | switches |", "|---|---|---|"]
    for name, block in (data.get("gnn_multi_bs") or {}).items():
        lines.append(
            f"| `{name}` | {_ci_cell(block, 'mean_snr_db')} | {fmt((block.get('n_beam_switches') or {}).get('mean'))} |"
        )
    lines += ["", "## Adaptive tracking", "", "| policy | SNR dB mean [95% CI] | probes | switches |", "|---|---|---|---|"]
    for name, block in (data.get("adaptive_tracking") or {}).items():
        lines.append(
            f"| `{name}` | {_ci_cell(block, 'mean_snr_db')} | {fmt((block.get('probes_used') or {}).get('mean'))} | {fmt((block.get('n_beam_switches') or {}).get('mean'))} |"
        )
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    tex.write_text(
        "\\textbf{Additive FR2 arms (SYNTHETIC\\_SIM).} "
        "See \\texttt{paper/tables/rq2\\_additive.md}. Sub-ms is TARGET, not proven.\n",
        encoding="utf-8",
    )
    print("wrote", md)


def write_sub6() -> None:
    src = EXP / "rq2_sub6_fr1_heldout.json"
    if not src.exists():
        src = EXP / "rq2_sub6_fr1_train.json"
    md = TABLES / "rq2_sub6.md"
    tex = TABLES / "rq2_sub6.tex"
    if not src.exists():
        pending(tex, "Missing Sub-6 JSON.")
        md.write_text("**RESULT_PENDING.** Missing Sub-6 JSON. Do not conclude.\n", encoding="utf-8")
        return
    data = json.loads(src.read_text(encoding="utf-8"))
    lines = [
        "# rq2_sub6 (SYNTHETIC_SIM, HOST_PROCESS_TIMING, n77 3.75 GHz FR1, NEVER 28 GHz)",
        "",
        f"carrier_hz={data.get('carrier', {}).get('frequency_hz')} profile={data.get('primary_profile')}. Not OTA.",
        "",
        f"FSPL gap vs 28 GHz (digital): {data.get('fspl_gap_vs_28ghz_db')} dB. "
        f"UMa-NLOS 35 m n77={data.get('uma_pl_35m_n77_db')} dB vs n257={data.get('uma_pl_35m_n257_db')} dB.",
        "",
        "| family | SNR dB mean [95% CI] | path loss dB | Doppler Hz | carrier_hz |",
        "|---|---|---|---|---|",
    ]
    for fam, block in (data.get("families") or {}).items():
        m = block.get("metrics") or {}
        snr = m.get("snr_exhaustive_db") or {}
        pl = m.get("path_loss_db") or {}
        fd = m.get("doppler_hz") or {}
        lines.append(
            f"| `{fam}` | {fmt(snr.get('mean'))} [{fmt(snr.get('ci_low'))}, {fmt(snr.get('ci_high'))}] | "
            f"{fmt(pl.get('mean'))} | {fmt(fd.get('mean'))} | {block.get('carrier_hz')} |"
        )
    lines += ["", "## Supporting true-below-6 GHz profiles", "", "| profile | carrier_hz | SNR dB |", "|---|---|---|"]
    for pid, block in (data.get("supporting") or {}).items():
        snr = ((block.get("metrics") or {}).get("snr_exhaustive_db") or {})
        lines.append(f"| `{pid}` | {block.get('carrier_hz')} | {fmt(snr.get('mean'))} |")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    tex.write_text(
        "\\textbf{Sub-6 n77 digital results (SYNTHETIC\\_SIM).} Not 28 GHz. Not OTA.\n",
        encoding="utf-8",
    )
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from sim.channels.sub6 import uma_nlos_pathloss_db

        fig, ax = plt.subplots(figsize=(6.2, 3.6))
        names = ["n71", "n41", "n77", "n257 FR2"]
        pls = [
            uma_nlos_pathloss_db(35.0, 0.6805e9),
            uma_nlos_pathloss_db(35.0, 2.593e9),
            float(data.get("uma_pl_35m_n77_db")),
            float(data.get("uma_pl_35m_n257_db")),
        ]
        ax.bar(names, pls, color=["#4C78A8", "#4C78A8", "#4C78A8", "#F58518"])
        ax.set_ylabel("UMa-NLOS PL at 35 m (dB)")
        ax.set_title("Digital path loss vs carrier (TR 38.901 UMa-NLOS; not OTA)")
        ax.grid(True, axis="y", alpha=0.3)
        fig.tight_layout()
        fig.savefig(FIGS / "rq2_sub6_pathloss.png", dpi=150)
        plt.close(fig)
    except Exception:
        pass
    print("wrote", md)


def write_dualband() -> None:
    src = EXP / "rq2_dualband_heldout.json"
    if not src.exists():
        src = EXP / "rq2_dualband_train.json"
    md = TABLES / "rq2_dualband.md"
    tex = TABLES / "rq2_dualband.tex"
    csv_path = TABLES / "rq2_dualband.csv"
    if not src.exists():
        pending(tex, "Missing dual-band JSON.")
        md.write_text("**RESULT_PENDING.** Missing dual-band JSON. Do not conclude.\n", encoding="utf-8")
        return
    data = json.loads(src.read_text(encoding="utf-8"))
    rows = []
    for row in data.get("rows") or []:
        u = row.get("min_useful_service_rate") or {}
        rows.append(
            {
                "policy": row.get("policy"),
                "failure": row.get("failure"),
                "device": row.get("device"),
                "workload": row.get("workload"),
                "min_useful_mean": u.get("mean"),
                "min_useful_ci_low": u.get("ci_low"),
                "min_useful_ci_high": u.get("ci_high"),
                "switch_rate": (row.get("switch_rate") or {}).get("mean"),
                "interruption_ms": (row.get("interruption_ms") or {}).get("mean"),
                "outage_rate": (row.get("outage_rate") or {}).get("mean"),
            }
        )
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["policy"])
        w.writeheader()
        w.writerows(rows)
    lines = [
        "# rq2_dualband (SYNTHETIC_SIM, min-useful service, n77 + n257)",
        "",
        "28 GHz remains FR2. Sub-6 is n77 3.75 GHz. Not OTA. Negative results valid.",
        "",
        "| policy | failure | device | workload | min-useful mean [95% CI] | switch | interrupt_ms | outage |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        ci = f"{fmt(r['min_useful_mean'])} [{fmt(r['min_useful_ci_low'])}, {fmt(r['min_useful_ci_high'])}]"
        lines.append(
            f"| `{r['policy']}` | `{r['failure']}` | `{r['device']}` | `{r['workload']}` | {ci} | "
            f"{fmt(r['switch_rate'])} | {fmt(r['interruption_ms'])} | {fmt(r['outage_rate'])} |"
        )
    gnn = data.get("gnn_audit") or {}
    rl = data.get("rl_audit") or {}
    lines += [
        "",
        "## GNN / RL audit",
        "",
        f"- heuristic GNN: `{gnn.get('sim.models.gnn_multi_bs')}`",
        f"- trainable GNN: `{gnn.get('sim.models.gnn_trainable')}`",
        f"- tabular RL: `{rl.get('adaptive_constrained_rl')}`",
        f"- sequential: `{rl.get('sequential_band_policy')}`",
        "",
        f"Trained GNN SNR dB: {fmt((data.get('gnn_trained') or {}).get('mean_snr_db'))} (SYNTHETIC_SIM).",
    ]
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    tex.write_text(
        "\\textbf{Dual-band min-useful service (SYNTHETIC\\_SIM).} See \\texttt{paper/tables/rq2\\_dualband.md}.\n",
        encoding="utf-8",
    )
    print("wrote", md)


def main() -> int:
    write_policy_table(
        TRAIN,
        "rq2_beam_train_policies",
        "Train-family FR2 TDL beam policies (SYNTHETIC\\_SIM; HOST\\_PROCESS\\_TIMING; 28 GHz FR2 not Sub-6).",
    )
    write_policy_table(
        HELD,
        "rq2_beam_heldout_policies",
        "Held-out FR2 TDL beam policies (SYNTHETIC\\_SIM; HOST\\_PROCESS\\_TIMING; 28 GHz FR2 not Sub-6).",
    )
    write_shift()
    write_ablation()
    write_figures()
    write_additive()
    write_sub6()
    write_dualband()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
