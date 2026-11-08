# Dataset

`defects_android.json`, `defects_harmony.json`, `defects_linux.json` are the
1,500 defect records released with

> Hongyao Zuo, Jiali Li, Jiajun Jiang. *Toward Understanding Operating System
> Defects.* arXiv:2608.20643v1, 2026.

They were exported from the authors' public dashboard
<https://zuohongyao.github.io/> on 2026-11-05; `PROVENANCE.json` records the
SHA-256 of the dashboard page and of each file at that moment.

Each record has the following fields:

| Field | Example | Used for |
| --- | --- | --- |
| `Bug ID` | `A-232799171` | uniqueness check |
| `Severity Level` | `High` | Table II panel 4 |
| `OS Layer` | `System Service Layer` | Table II panel 1, Table III/IV rows |
| `Affected Function` | `Security and Permission Control` | Table II panel 2, Table III/V |
| `Trigger Scenario` | `Regular Operation Trigger` | Table II panel 3, Table IV/V |
| `Code Level` | `Function Call, Assignment` | Table II panel 5 (multi-label) |
| `Line Deletions/Additions/Changes` | `2 / 1 / 3` | Figure 2 (`Line Changes`) |
| `Involved Functions`, `Modified Files` | `0 / 1` | Figure 3 |
| `Patch` | URL | not analysed |

The labels are the authors' own; this replication does not re-label the
patches (see `docs/DEVIATIONS.md`, D1).  The records are redistributed here for
academic reproduction only, with attribution.  All rights remain with the paper's
authors.

`paper/` holds machine-readable copies of the numbers printed in the paper,
transcribed from the arXiv HTML version and the figure assets; see
`paper/README.md`.
