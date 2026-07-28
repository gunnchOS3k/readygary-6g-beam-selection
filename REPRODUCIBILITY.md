        # Reproducibility — ReadyGary 6G Beam Selection

        ## Clone / setup / run

        ```bash
        git clone https://github.com/gunnchOS3k/{name}.git
cd readygary-6g-beam-selection
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q
# Expected: CI smoke pass; tests pass or documented skip
        ```

        ## Expected outputs

        - Required documentation files present (`python3 scripts/check_required_files.py`)
        - Tests pass **or** documented smoke-only path for docs-only repos
        - No claim of field deployment from synthetic outputs alone

        ## Tool versions

        | Tool | Version guidance |
        |------|------------------|
        | Python | 3.10+ where `requirements.txt` exists |
        | Node | 18+ LTS where `package.json` exists |
        | Make | GNU Make where `Makefile` exists |

        Record exact versions in PR / release notes when publishing.

        ## Fresh machine checklist

        - [ ] Clone repo
        - [ ] Create clean venv / `npm ci`
        - [ ] Run `scripts/check_required_files.py`
        - [ ] Run test command from README
        - [ ] Compare outputs to `results/` or CI logs
        - [ ] Log environment in `reproducibility/FRESH_MACHINE_LOG.md` (optional)

        ## Evidence discipline

        **Real today:** Algorithms, tests, documentation

        **Synthetic / demo-only:** Benchmark tables

        **Planned:** Hardware-in-loop validation

        **Not claimed:** Certified 6G hardware
