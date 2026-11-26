# Files changed in this round (layer-composition task)

Added on 2026-11-26, relative to this directory.  Nothing outside
`wenruibao1240016315/` is modified; the shared dataset and the baseline
directory are read-only from here.

## New code

| File | Purpose |
| --- | --- |
| `scripts/layer_analysis.py` | the whole analysis: composition, within-layer tables, standardisation, distances, figures |
| `scripts/run_layer_triplicate.py` | runs the analysis three times in isolated directories, hashes every output, writes `results/determinism.json` |
| `tests/test_layer_rules.py` | 12 unit tests: distance metric, composition, support rule, explained arithmetic, dataset consistency |

## New result tables (under `results/`)

| File | Rows |
| --- | ---: |
| `layer_composition.csv` | 18 |
| `layer_within_function.csv` | 144 |
| `layer_within_trigger.csv` | 126 |
| `layer_pairwise_function.csv` | 15 |
| `layer_pairwise_trigger.csv` | 15 |
| `layer_distances.csv` | 6 |
| `determinism.json` | three-run hash comparison |
| `logs/layer_run{1,2,3}/` | per-run tables, figures, stdout log, run metadata |

## New figures (under `figures/`)

`layer_composition.png` / `.svg`, `layer_distance_adjustment.png` / `.svg`.

## New documents (under `docs/`)

`METHODS.md`, `DEVIATIONS.md`, `MEMBER_CONTRIBUTION.md`, `AI_USAGE.md`,
`FILES_CHANGED.md`, `GROUP_INTEGRATION.md`, `LAYER_ANALYSIS.md`,
`LAYER_ONE_PAGER.md`, `SUBMISSION.md`; and `results/REPORT.md`.

## Modified

| File | Change |
| --- | --- |
| `Makefile` | added `layer`, `layer-triplicate`, `test` targets |
| `README.md` | added the layer task to the folder description and the run instructions |
| `.gitignore` | ignores `results/logs/run*/` and `figures/logs/run*/` |
