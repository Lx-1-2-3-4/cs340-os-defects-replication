# Member contribution

**Member:** 熊耀鹏  
**Student ID:** 1230019796  
**Folder:** `xiongyaopeng1230019796/`

## Baseline

This independent member folder copies the group's existing Liu Xin submission
at starting commit `743badb`. The dataset, labels, original reproduction
pipeline, MIT license, and existing sample-size and missing-severity extensions
are baseline material and are attributed to that source project.

## New contribution

The Figure 4(a-c) bootstrap uncertainty experiment is the contribution prepared
for this member:

- `extension/figure4_bootstrap.py`: stratified record-bootstrap of the nine
  cross-OS Spearman coefficients, with deterministic seed and paper-value check.
- `extension/results/figure4_bootstrap.csv`: coefficient intervals and
  resampling stability metrics from 10,000 replicates.
- `extension/results/figure4_bootstrap.md`: design, results, environment,
  dataset hashes, and limitations.
- `Makefile`, `README.md`, `extension/README.md`, and `docs/CLAIMS.md`: integrate
  and document the experiment in this member's submission.

The report states that four of the nine intervals exclude zero and explains
that the intervals measure sensitivity in the selected dataset rather than
population-level uncertainty.
