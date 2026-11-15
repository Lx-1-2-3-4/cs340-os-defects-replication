# Contribution statement material (Wen Ruibao, 1240016315)

Use this page when writing the group report's contribution statement.  It
describes what this folder contains and what it adds beyond the main
implementation.

## Contribution

**Independent second implementation of the full quantitative replication.**
Wrote a separate implementation (data loading, label mapping, aggregation,
histograms, Spearman correlation) from the paper's definitions, sharing no
source file with `../liuxin1240013249/scripts/`.  It reproduces all 600
reproducible printed values.

**Cross-implementation verification.**  Added `scripts/crosscheck.py`, which
joins the two implementations' result tables on the paper keys and checks both
percentages and the underlying defect counts.  Result: 603/603 values and
591/591 counts identical.  This is the evidence that the numbers do not depend
on one implementation, and that the Figure 4d gap is a property of the paper
rather than a bug.

**Metric-sensitivity extension (C5).**  Designed and ran the Jensen–Shannon
extension that tests whether the paper's cross-system similarity conclusion is
an artefact of Spearman's rank correlation: all twelve comparisons remain far
apart (JSD 0.388–0.688), but the pair ordering changes in half the slots.

**Figure 4d rule search.**  Implemented and documented eight candidate rules for
the under-specified “overall” panel; none reproduces the printed coefficients,
and the paper's text disagrees with its own heatmap about the −0.11 value.

**Reproducibility packaging.**  Dockerfile, Makefile, three-run determinism
check, dataset provenance, self-validating result files.

## Files

| Area | Files |
| --- | --- |
| Implementation | `scripts/common.py`, `scripts/reproduce.py`, `scripts/compare.py`, `scripts/validate.py` |
| Verification | `scripts/crosscheck.py`, `results/crosscheck.csv`, `results/CROSSCHECK.md` |
| Extension | `scripts/extension.py`, `results/extension_jsd.csv` |
| Figure 4d analysis | `scripts/fig4d_candidates.py`, `results/fig4d_candidates.csv`, `docs/DISCREPANCIES.md` |
| Reproducibility | `Dockerfile`, `Makefile`, `scripts/triplicate.py`, `data/PROVENANCE.json` |
