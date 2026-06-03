from pathlib import Path

def write_registry(out: Path | None = None) -> Path:
    out = out or Path("results/tool_exports/benchmark_dataset_registry.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("# Benchmark registry\n\n| Source | Status |\n|--------|--------|\n| toy smoke | active |\n| DeepMIMO | config only |\n| Sionna | config only |\n", encoding="utf-8")
    return out
