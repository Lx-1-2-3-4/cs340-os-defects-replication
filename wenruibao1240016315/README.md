# CS340 replication — Wen Ruibao (1240016315)

Replication of

> Hongyao Zuo, Jiali Li, Jiajun Jiang. **Toward Understanding Operating System
> Defects.** arXiv:2608.20643v1, 2026. <https://arxiv.org/abs/2608.20643>

Data: the defect records released by the authors at
<https://zuohongyao.github.io/> (snapshot of 2026-11-05, see
`data/PROVENANCE.json`).

This folder recomputes every quantitative value printed in the paper from the
1,500 released defect records and compares the result, value by value, with the
paper.  The dataset snapshot, the transcribed paper values, the analysis code
and the generated output are committed, so the whole comparison runs offline
with the Python standard library only.

## Results

| Paper item | Values compared | Matched |
| --- | ---: | ---: |
| Table II (five distributions) | 114 | 114 |
| Table III (OS layer × affected function) | 144 | 144 |
| Table IV (OS layer × trigger scenario) | 126 | 126 |
| Table V (affected function × trigger scenario) | 168 | 168 |
| Figure 2 (changed code lines) | 15 | 15 |
| Figure 3 (involved functions / modified files) | 24 | 24 |
| Figure 4 (cross-system Spearman coefficients) | 12 | 9 |
| **Total** | **603** | **600 (99.50 %)** |

Panels (a)–(c) of Figure 4 reproduce exactly.  The three coefficients of panel
(d), the under-specified “overall” panel, do not; the paper's own text and
heatmap also disagree about that panel.  See [`docs/DISCREPANCIES.md`](docs/DISCREPANCIES.md).

Every value is in `results/comparison.csv` (paper value, our value, the defect
count behind it and a match flag).  `results/check.json` has the per-item totals.

## Running it

Run from this folder.  Python 3.10+ with no third-party packages.

```bash
python scripts/reproduce.py     # recompute the 603 values -> results/*.csv
python scripts/compare.py       # compare with the paper -> results/comparison.csv
python scripts/validate.py      # self-check: 603 values, 600 matches, only Fig. 4d differs
```

Optional:

```bash
python scripts/triplicate.py    # three runs, hash every output, prove determinism
python scripts/extension.py     # extension: Spearman vs Jensen-Shannon
python scripts/fig4d_candidates.py   # the Figure 4d rule search
```

`make all`, `make validate`, `make triplicate`, `make extension` run the same
commands; `make` is optional (on Windows without make, use the Python commands).

Docker:

```bash
docker build -t cs340-os-defects:1.0 .
docker run --rm cs340-os-defects:1.0
```

## What is and is not reproduced

Reproduced: the aggregation of the released labels into Tables II–V and
Figures 2–4, i.e. every number that the paper derives from the 1,500 records.

Not reproduced: the **labelling** of the 1,500 patches (two annotators,
Cohen's kappa 0.8–1.0), the collection funnel of Table I (32,249 Linux /
712 HarmonyOS / 1,750 Android initial reports), and the qualitative taxonomy of
Figure 1.  The authors released the labelled records but not the raw candidate
pool or the annotation protocol, so these steps cannot be rebuilt from public
data.  Exact agreement on Tables II–V therefore checks the label-to-table
mapping, the aggregation rules and the transcription — not the labels
themselves.

## Extension

`scripts/extension.py` asks whether the cross-system similarity conclusion is an
artefact of the metric.  Spearman's rho is rank-based and ignores magnitudes;
the Jensen–Shannon distance between the percentage distributions does not.
Result: all twelve panel/pair comparisons stay far apart (JSD 0.39–0.69) under both metrics, so the
“systems behave differently” conclusion is robust, but the *ordering* of the
three pairs changes in 6 of the 12 panel/pair ranks, so statements about which
two systems are most alike are metric-dependent.  Details in
`results/extension_jsd.csv` and `docs/CLAIMS.md` (C5).

## Layout

```
data/       defect snapshot, provenance, transcribed paper values
scripts/    dataset loading, recomputation, comparison, validation, extension
results/    generated CSVs, comparison table, run logs
docs/       claims and verdicts, deviations, Figure 4d analysis
```

## Deviations

Every difference from the paper's setup — the labelling step we could not
repeat, the multi-label denominator, the Figure 4 panel-(d) rule, the histogram
bucket boundaries, the HarmonyOS `Unknown` severity labels — is listed with the
paper's setting, the setting used here and the reason in
[`docs/DEVIATIONS.md`](docs/DEVIATIONS.md).

## Environment

The pipeline is pure data analysis.  The committed results were produced on
Windows 11 with CPython 3.14.7 (see `results/summary.json` for the exact run).
The Dockerfile pins `python:3.12.7-slim` so the environment is reproducible on a
clean machine.

## Data and licence

The defect records belong to the paper's authors and are redistributed here for
academic reproduction only, with attribution (see `data/README.md`).  The code
in this folder is MIT licensed (`LICENSE`).
