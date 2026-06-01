# Problem → Solution Map — ReadyGary — 6G Beam Selection

## The human problem
Dropped links and poor video calls when beams point the wrong way in dense or mobile environments.

Who is harmed: Users on mmWave at the cell edge; researchers who need reproducible PHY evidence.

## The technical problem
Beam selection under mobility/blockage with rigorous baselines—not marketing claims without latency proof.

## The research gap
Existing tools rarely combine **equity**, **open reproducibility**, and **cross-repo evidence** for under-connected communities at Gary-scale fidelity.

## This repo's solution
Baselines (exhaustive/heuristic), ML trackers, benchmark scripts, LaTeX paper CI—smoke tables until realistic channels + hardware timing exist.

## What runs today
`make smoke` → `results/e2e/benchmark_table.md`

## What the output means
Smoke-test artifact for CI and portfolio review.

## What the output does NOT prove
Proven sub-ms edge inference or production-ready deployment.

## How a researcher can extend it
Pick one `next_evidence` item; document benchmark or field protocol; link PR to `[Evidence TODO]` issue.

## How a WAIKE learner can contribute
Run smoke test · file reproduction issue · fix docs/tests · pair with mentor on one evidence issue.
