# CS340 replication — independent verification track

Replication of

> Hongyao Zuo, Jiali Li, Jiajun Jiang. **Toward Understanding Operating System
> Defects.** arXiv:2608.20643v1, 2026. <https://arxiv.org/abs/2608.20643>

Data: the 1,500 defect records released by the authors at
<https://zuohongyao.github.io/> (snapshot of 2026-11-05, see
`data/PROVENANCE.json`).

## What this folder is

The group's main implementation is in [`../liuxin1240013249/`](../liuxin1240013249/);
it establishes the numbers and carries the claim/deviations documents that the
final report is built from.  This folder is the **second, independently written
implementation** of the same 603 values.  It does not restate the paper's
claims, and it is not a second copy of the main pipeline: its job is to show
that the results are a property of the dataset rather than of one person's code.

Three things are unique to this folder:

1. **An independent implementation.** `scripts/` shares no source file with the
   main implementation — different structure, different helpers, written from
   the paper's definitions.  It reproduces 600/603 printed values and, more
   importantly, agrees with the main implementation on **603/603** values.
2. **A cross-implementation check** (`scripts/crosscheck.py`, `results/CROSSCHECK.md`).
   Two independent implementations producing the same 603 values, including the
   three Figure 4d coefficients that differ from the paper, is evidence that the
   Figure 4d discrepancy is a specification gap in the paper and not a bug in
   either implementation.
3. **A metric-sensitivity extension** (`scripts/extension.py`).  The paper's
   cross-system comparison uses Spearman's rho, which only sees the order of the
   categories.  The extension repeats the comparison with the Jensen–Shannon
   distance, which also sees magnitudes.

The 8-rule search for the under-specified Figure 4d panel
(`scripts/fig4d_candidates.py`) is also kept here, because it supports the same
point: no plausible reading of the panel reproduces the printed coefficients.

## Results

| Check | Values | Result |
| --- | ---: | ---: |
| Printed values reproduced from the dataset | 603 | 600 (99.50 %) |
| Values identical to the main implementation | 603 | **603 (100 %)** |
| Defect counts identical to the main implementation | 591 | **591 (100 %)** |

The three values that do not match the paper are the three coefficients of
Figure 4d.  Both implementations compute the same values for them
(0.16 / 0.08 / 0.05 against the printed 0.05 / −0.11 / −0.04), which is the
point of the cross-check.

Per-value data: `results/comparison.csv` (against the paper) and
`results/crosscheck.csv` (against the main implementation).

## Running it

Run from this folder.  Python 3.10+, no third-party packages.

```bash
python scripts/reproduce.py     # recompute the 603 values -> results/*.csv
python scripts/compare.py       # compare with the printed paper values
python scripts/validate.py      # self-check: 603 values, 600 matches, only Fig. 4d differs
python scripts/crosscheck.py --main ../liuxin1240013249/results   # compare with the main implementation
```

Optional:

```bash
python scripts/triplicate.py    # three runs, hash every output (determinism)
python scripts/extension.py     # Spearman vs Jensen-Shannon
python scripts/fig4d_candidates.py   # the Figure 4d rule search
```

`make all`, `make crosscheck`, `make extension` run the same commands; `make` is
optional.

`crosscheck.py` needs the sibling folder of the main implementation, so it works
inside the group repository and is skipped when this folder is used on its own.

## Extension in one paragraph

All twelve panel/pair comparisons stay far apart under both metrics (Jensen–
Shannon distance 0.388–0.688, where 0 means identical distributions), so the
paper's qualitative conclusion — the three systems behave differently — does not
depend on the choice of similarity measure.  The *ordering* of the three pairs,
however, changes in 6 of the 12 panel/pair slots, so statements about which two
systems are most alike should name the metric.  Details in
`results/extension_jsd.csv`.

## Layout

```
data/       defect snapshot, provenance, transcribed paper values
scripts/    independent implementation, comparison, cross-check, extension
results/    generated CSVs, cross-check table, run log
docs/       verification notes, implementation-specific notes, Figure 4d analysis
```

## Relation to the group report

* Claims and verdicts for the report: `../liuxin1240013249/docs/CLAIMS.md`.
* Dataset-level deviations (labelling, collection, bucket boundaries):
  `../liuxin1240013249/docs/DEVIATIONS.md`.
* This folder's notes: `docs/VERIFICATION.md` (what was checked here),
  `docs/NOTES.md` (implementation-specific decisions) and
  `docs/DISCREPANCIES.md` (Figure 4d).
* Report text ready to merge: `docs/REPORT_DRAFT.md` (C3, Figure 4d, the
  extension) and `docs/SLIDES.md` (three-slide outline for the presentation).
* Contribution statement material: `docs/CONTRIBUTION.md`.

## What is not reproduced

The manual labelling of the 1,500 patches, the collection funnel of Table I and
the qualitative taxonomy of Figure 1.  The authors released the labelled records
but not the candidate pool or the annotation protocol; exact agreement on
Tables II–V therefore checks the mapping and aggregation, not the labels.  This
limitation is shared with the main implementation and is recorded once, in the
group's deviations document.

## Environment

Pure data analysis, standard library only.  The committed results were produced
on Windows 11 with CPython 3.14.7 (see `results/summary.json`).  The Dockerfile
pins `python:3.12.7-slim`.

## Data and licence

The defect records belong to the paper's authors and are redistributed for
academic reproduction only, with attribution (`data/README.md`).  The code in
this folder is MIT licensed (`LICENSE`).
