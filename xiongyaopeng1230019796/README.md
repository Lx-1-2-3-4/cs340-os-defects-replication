# CS340 replication — 熊耀鹏 (1230019796)

Course project for CS340 Operating Systems (2026–2027).

This member submission starts from the group's Liu Xin baseline at commit
`743badb`. The independent contribution in this folder adds a record-bootstrap
uncertainty analysis for Figure 4(a-c); see
[`docs/MEMBER_CONTRIBUTION.md`](docs/MEMBER_CONTRIBUTION.md) for file-level
attribution.

Paper: Hongyao Zuo, Jiali Li, Jiajun Jiang. "Toward Understanding Operating
System Defects." arXiv:2608.20643v1, 2026.

Data: the defect records released by the authors at
<https://zuohongyao.github.io/>.

This repository recomputes the quantitative results of the paper from the 1,500
released defect records and compares them, value by value, with what is printed
in arXiv v1. The dataset snapshot, the transcribed paper values, the analysis
scripts and the generated output are all committed, so the comparison can be run
offline.

## Results

| Paper item | Values compared | Matched |
| --- | ---: | ---: |
| Table II (five distribution panels) | 114 | 114 |
| Table III (OS layer × affected function) | 144 | 144 |
| Table IV (OS layer × trigger scenario) | 126 | 126 |
| Table V (affected function × trigger scenario) | 168 | 168 |
| Figure 2 (changed code lines) | 15 | 15 |
| Figure 3 (involved functions / modified files) | 24 | 24 |
| Figure 4 (cross-OS Spearman coefficients) | 12 | 9 |
| **Total** | **603** | **600 (99.50%)** |

The nine coefficients of Figure 4 panels (a)–(c) reproduce exactly. The three
coefficients of panel (d) do not reproduce, and the paper's text and heatmap
disagree about which pair the −0.11 value belongs to. Both points are written up
in [`docs/DISCREPANCIES.md`](docs/DISCREPANCIES.md).

Per-value comparisons are in [`results/`](results/), one CSV row per value with
the paper value, our value, the defect count behind it and a match flag.
[`results/SUMMARY.md`](results/SUMMARY.md) is a one-page version of the table
above.

## Running it

All commands below are run from this folder (`liuxin1240013249/`). Everything uses
the Python standard library only. The last run was CPython 3.14.6 on Windows 11;
the Dockerfile pins 3.12.7.

```bash
python scripts/fetch_data.py --check     # check the snapshot against data/PROVENANCE.json
python scripts/run_triplicate.py         # run reproduce.py three times, check the output is identical
python scripts/validate_results.py       # compare with results/expected_summary.json
```

`make reproduce` and `make validate` run the same two steps. The whole thing takes
a few seconds. (`make` is optional: on Windows without make, use the Python
commands above.)

Docker:

```bash
docker build -t cs340-os-defects:1.0 .
docker run --rm -v "${PWD}/results:/work/results" cs340-os-defects:1.0
```

The committed snapshot is enough for the reproduction. To refresh it from the
live dashboard:

```bash
python scripts/fetch_data.py                  # rewrite data/defects_*.json and PROVENANCE.json
python scripts/fetch_data.py --check --verify-remote   # also compare with the live page
```

## What the scripts do

`scripts/fetch_data.py` downloads the dashboard page, pulls the three defect
arrays out of the embedded `var DATA = {...}` object, validates them, and records
the page hash and per-file hashes in `data/PROVENANCE.json`.

`scripts/reproduce.py` loads the snapshot, translates the dashboard's long
category names to the short names used in the paper, computes each table and
figure value, and writes the results as CSV.

`scripts/run_triplicate.py` runs the pipeline three times and hashes every output
file, so a change in the output between runs would be visible in
`results/logs/`. `scripts/validate_results.py` compares the totals with
`results/expected_summary.json`.

The values printed in the paper were transcribed into `data/paper/` (see
[`data/paper/README.md`](data/paper/README.md)) so the comparison runs offline.

## Definitions worth knowing

- `Code Level` is multi-label. A defect is counted once for every tag in its
  comma-separated value, and percentages are taken over 500 (deviation D3).
- For Figure 4c, categories that are zero for both systems of a pair are dropped
  before computing Spearman's rho. Without this rule Android–HarmonyOS gives
  0.61 instead of the printed 0.38 (deviation D4).
- The Figure 2 and Figure 3 bucket boundaries are half-open and were inferred
  from the printed percentages (deviation D7).
- The "Overall" panel of Figure 4 is not described in the paper. We concatenate
  the 21 categories of panels (a)–(c) and apply the same zero rule (deviation
  D5). Five candidate rules are compared in
  `results/fig4_overall_candidates.csv`.

All deviations from the paper's setup, with the paper's setting, the setting used
here and the reason, are in [`docs/DEVIATIONS.md`](docs/DEVIATIONS.md).

## What is not reproduced

The released records already contain the authors' labels, so this covers the
analysis but not the measurement. We did not re-label the 1,500 patches, and the
collection funnel of Table I (32,249 Linux / 1,750 Android / 712 HarmonyOS
initial reports) cannot be rebuilt from the released files. Figure 1's taxonomy
and the paper's discussion sections are qualitative and are not checked here.

Because the input labels are the authors' own, exact agreement on the tables is
what correct aggregation should produce. The comparison therefore tests the
label-to-table mapping, the aggregation rules and the transcription of the paper
values. It does not test the labels themselves, and the one result that does not
match (Figure 4d) is more informative than the 600 that do.

## Extension

Three follow-up experiments use the same dataset and label mappings as the reproduction.
[`extension/README.md`](extension/README.md) has
the design and the full results; in short:

- **Sample-size sensitivity.** Subsampling the 500 defects per system down to
  n = 100 keeps 11 of the 15 (OS, dimension) top categories stable. HarmonyOS
  affected function, Linux code elements and Android trigger scenario become
  sample-size dependent. Bootstrap intervals for all 114 Table II percentages
  are in `extension/results/table2_bootstrap_ci.csv`.
- **Missing severity labels.** Linux has 65.20% `Undecided` severity records;
  excluding them moves the top Linux category from `Undecided` to `High`
  (18.60% → 53.45% of the labelled subset).
- **Figure 4 correlation uncertainty.** All nine point estimates in panels
  (a)–(c) reproduce the paper. In 10,000 record-level bootstrap draws, four of
  the nine 95% intervals exclude zero; the other five remain uncertain. The
  bootstrap is conditional on the released sample and does not justify
  population-level generalization.

Run `make extension`, or the scripts directly from this folder.

## Repository layout

```
data/       dataset snapshot, provenance, transcribed paper values
scripts/    fetch, reproduce, three-run check, validation
extension/  three extension experiments and their results
results/    generated CSVs, summary, run logs
docs/       claims, deviations, Figure 4d discrepancy analysis
```

## Data and licence

The defect records belong to the paper's authors and are redistributed here for
academic reproduction only, with attribution; see
[`data/README.md`](data/README.md). The code is under the MIT licence
([`LICENSE`](LICENSE)).
