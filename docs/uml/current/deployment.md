# Deployment — current execution surfaces

| | |
|---|---|
| **Status** | **Current** — honest about the empty `deploy/` directory |
| **Purpose** | Where Python, pytest, and GitHub Actions actually run. |

```mermaid
flowchart LR
  subgraph laptop["Experimenter workstation"]
    PY[Python 3 + pytest]
    MK[make test / benchmark-toy / timing / reproduce]
  end

  subgraph gh["GitHub"]
    LATEX[.github/workflows/latex.yml]
    CI[.github/workflows/ci.yml]
    SRC[gunnchOS3k/readygary-6g-beam-selection]
  end

  subgraph artifacts["Committed or generated"]
    RES[results/* SYNTHETIC_SIM]
    PAPER[paper/main.tex PDF artifact]
  end

  subgraph absent["Not in this checkout"]
    DOCK[Docker / FastAPI / gRPC]
    EDGE[ONNX Runtime service]
  end

  PY --> MK
  MK --> RES
  SRC --> LATEX
  SRC --> CI
  LATEX --> PAPER
  CI --> PY
  DOCK -.->|README historical claim| absent
```

Edge service commands in the README (`docker build`, `/v1/infer`) describe a **future** path. There is no `deploy/` payload to build today.

[← Current index](index.md)
