# Member contribution — Wen Ruibao (1240016315)

## Role in the group

Owner of the layer-composition analysis ("层级构成对跨操作系统缺陷分布差异的影响")
and of the independent verification track.  This directory contains both, as
separate pieces so the report can use them independently.

## What was done for the layer task

1. **Problem framing.**  Turned the assigned question into a testable design:
   composition table → within-layer comparison → standardisation (pooled and
   uniform weights) → before/after distance comparison.
2. **Implementation.**  `scripts/layer_analysis.py`: label mapping reuse, layer
   counting, within-layer distributions, direct standardisation, Jensen–Shannon
   distance, support rule, two figures (PNG + SVG).
3. **Robustness choices.**  Minimum-support rule (≥ 10 defects in all three
   systems) fixed before looking at the results; `RuntimeVM` excluded and
   reported; two weight sets instead of one; negative "explained" values kept
   rather than clipped, which is what revealed the Simpson-type effect.
4. **Evidence.**  Six result tables, two figures, a three-run determinism check
   with hashes, and twelve unit tests.
5. **Write-up.**  `docs/METHODS.md`, `docs/DEVIATIONS.md`, `docs/LAYER_ANALYSIS.md`,
   the one-page English summary (`docs/LAYER_ONE_PAGER.md`) and the report-ready
   paragraphs.

## What was done for the verification track

* A second, independently written implementation of the 603-value replication
  (`scripts/common.py`, `reproduce.py`, `compare.py`, `validate.py`), sharing no
  source file with the main implementation.
* `scripts/crosscheck.py`: joins the two implementations' outputs on the paper
  keys — **603/603 values and 591/591 counts identical**, which is the evidence
  that the Figure 4d mismatch is a property of the paper.
* The Jensen–Shannon metric-sensitivity extension (`scripts/extension.py`) and
  the eight-rule search for the under-specified Figure 4d panel
  (`scripts/fig4d_candidates.py`).

## Attribution

* Defect records, labels and the reference values: the paper's authors (Zuo, Li,
  Jiang, arXiv:2608.20643v1), redistributed under the terms described in
  `../data/README.md`.
* Data extraction, label vocabulary, paper transcription and the main
  implementation: the group baseline (`../liuxin1240013249/`).
* Code, tables, figures and text in this directory: Wen Ruibao, with the AI
  assistance declared in `AI_USAGE.md`.

## Deliverables map

| Requirement | File |
| --- | --- |
| Problem and method | `METHODS.md` |
| Data and provenance | `METHODS.md` §Data, `../data/PROVENANCE.json` |
| Runnable code | `../scripts/layer_analysis.py`, `../scripts/run_layer_triplicate.py` |
| Complete result tables | `../results/layer_*.csv` |
| Core figures | `../figures/layer_composition.*`, `layer_distance_adjustment.*` |
| Conclusion and limitations | `LAYER_ANALYSIS.md`, `METHODS.md` §Limitations |
| One-page English summary | `LAYER_ONE_PAGER.md` |
| Reused vs new | `GROUP_INTEGRATION.md` |
