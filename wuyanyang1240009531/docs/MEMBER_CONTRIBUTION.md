# Member contribution record

Member: **吴彦阳 — 1240009531 (Wu Yanyang)**.

This records the module prepared for the named student's review and submission.
It does not claim that AI-generated code was written unaided or that the student
has already completed personal review. See `AI_USAGE.md`.

## Added contribution

| Work | Reviewable evidence |
| --- | --- |
| Fixed-input data/schema/count audit with traceable IDs | `scripts/audit_data.py`, `results/data_audit.csv` |
| Two separate single-factor preprocessing contrasts | `scripts/run_sensitivity.py`, two comparison CSVs |
| Independent average-rank Spearman implementation | `scripts/core.py`, hand-calculated tests |
| Correct propagation of censored `10+` membership | `possible_buckets()`, bounds and record-level output |
| Three real runs, source/input hashes, mean/sample SD | `scripts/run_triplicate.py`, `results/logs/`, `runs/` |
| Cell-level verification and adversarial checks | `scripts/verify_results.py`, `tests/test_rules.py` |
| Charts and English analysis from computed output | `scripts/plot_results.py`, `results/REPORT.html` |
| Group integration | Own member index entry and isolated CI job |

The main new finding is that one Figure 4c interpretation changes with the
shared-zero policy, while first-bin dominance survives alternative endpoints
despite substantial percentage shifts and three censored counts. The arithmetic
warning provides a concrete example of an inconsistency invisible to aggregate
matching. These are additional checks, not a new defect collection.

## Reused work and boundaries

- **刘鑫 (1240013249):** baseline extraction, dataset/provenance, transcribed
  paper references, taxonomy and prior baseline/extension experiments. Inputs
  are read in place; they are not repackaged as this member's collection.
- **闻瑞宝 (1240016315):** existing independent aggregation and JSD analysis.
  These results and code are not reattributed to this contribution.
- **熊耀鹏 (1230019796):** existing attributed baseline reuse and Figure 4
  record-bootstrap extension. This module does not claim that bootstrap.
- **Paper authors:** original labelled dataset, defect taxonomy and findings.

No teammate analysis code is imported. Taxonomy constants and reference schemas
are restated with credit; independence is limited to implementation of this
module's statistics/checks, not independent data collection or annotation.
No existing teammate source/data file is changed by this contribution.

## Submission history

Local testing is not a GitHub push. Do not claim weekly remote contribution
until an actual authorized substantive push occurs. Later commit messages must
contain the student's actual ID and full name, for example:

`Add preprocessing sensitivity audit and reproducible evidence (1240009531 吴彦阳)`

Do not backdate commits, impersonate another author, or create empty commits
to simulate work. Final tagging and group submission remain group decisions.
