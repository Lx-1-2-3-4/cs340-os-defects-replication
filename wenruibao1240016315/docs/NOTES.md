# Implementation-specific notes

Dataset-level deviations (labelling not repeated, collection funnel not rebuilt,
multi-label denominator, histogram buckets, HarmonyOS `Unknown` severity) are
identical to the main implementation and are recorded once, in
`../../liuxin1240013249/docs/DEVIATIONS.md`.  This page lists only the decisions
that are specific to the verification track.

| ID | Item | Decision | Reason |
| --- | --- | --- | --- |
| V1 | Why a second implementation | Written from the paper's definitions without reading the main implementation's source; no shared file | A replication check is only meaningful if the two programs can fail independently |
| V2 | Cross-check reference | `../liuxin1240013249/results/*_reproduction.csv`, compared on the paper keys | The main implementation writes one row per printed value, which makes a value-by-value join possible |
| V3 | Comparison tolerance | Percentages and coefficients rounded to 2 decimals (as printed); defect counts compared as integers | Matches how the paper reports values; any difference in aggregation shows up in the counts first |
| V4 | Cross-check scope | Needs the sibling folder; skipped when this folder is used on its own | The check is about the group repository, not about the dataset alone |
| V5 | Extension design | Jensen–Shannon distance (base 2) between percentage distributions; categories kept as printed, no re-weighting | One factor changed at a time: only the similarity measure differs from the paper |
| V6 | Figure 4d rule search | Eight documented rules; the baseline is the same drop-shared-zeros rule used for panel (c) | Makes the "under-specified" claim checkable rather than assertive |
| V7 | Runs | Three full runs, every output hashed, byte-identical | The analysis is deterministic; the standard deviation is 0.00 by construction, shown rather than claimed |
| V8 | Environment | Windows 11 + CPython 3.14.7 locally, `python:3.12.7-slim` in Docker | Pinned interpreter; the pipeline has no third-party dependency |
