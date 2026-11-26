# Methods: layer composition as a confounder of cross-system differences

## Research question

The replication compares three systems (Android, Linux, HarmonyOS) on 500
released defects each.  The paper reports that the distributions of defect
attributes differ across systems (Table II) and that the joint distributions are
system-specific (Tables III–V).  The three samples, however, are not drawn from
comparable layer populations.  This study asks:

1. How different is the OS-layer composition of the three samples?
2. Inside the layers that all three systems share, do the systems still differ in
   affected function and trigger scenario?
3. After standardising each system to a common layer mix, how much of the raw
   cross-system difference remains?

## Data and provenance

Inputs are the group's pinned copy of the authors' released dataset
(`../data/defects_*.json`, 500 records per system), extracted from
<https://zuohongyao.github.io/> on 2026-11-05 and hashed in
`../data/PROVENANCE.json`.  The label vocabulary (six OS layers, eight affected
functions, seven trigger scenarios) and the mapping from the dashboard's long
labels to the paper's short labels are the group baseline's; this module restates
them with attribution and does not import any teammate analysis module.

No re-annotation, no new collection and no kernel or vulnerability execution:
this is a statistical re-analysis of the fixed snapshot.  Percentages and counts
are therefore exactly reproducible.

## Definitions

**Layer composition.**  For system `s` and layer `l`, `n(s,l)` is the number of
the 500 defects whose `OS Layer` is `l`; the share is `n(s,l) / 500`.

**Within-layer distribution.**  `P_s(c | l)` is the share of category `c`
(affected function or trigger scenario) among the defects of system `s` in layer
`l`, with the layer sample size `n(s,l)` reported alongside.

**Standardisation.**  Each system's marginal is rebuilt under a common layer mix
`w`:

```
P_std^s(c) = Σ_l  w_l · P_s(c | l)
```

Two weight sets are used and reported separately:

* *pooled* — `w_l` is layer `l`'s share of all 1,500 defects;
* *uniform* — every shared layer receives `1/L`.

**Distance.**  Jensen–Shannon distance with base-2 logarithm,
`JSD(P,Q) = sqrt(0.5·KL(P‖M) + 0.5·KL(Q‖M))`, `M = (P+Q)/2`, in [0,1]
(0 = identical, 1 = disjoint support).  It is a symmetric, bounded distance and
does not require the categories to be ordered.

**Within-layer average.**  `Σ_l w_l · JSD(P_s(·|l), P_t(·|l))`, the
layer-weighted average of the pairwise distances computed inside each layer.

**Explained share.**  `100 · (JSD_raw − JSD_std) / JSD_raw`.  A negative value
means the raw comparison *understates* the difference inside layers.

## Support rule and exclusions

A layer enters the within-layer and standardised comparisons only if it has **at
least 10 defects in all three systems**.  Five layers qualify: Kernel (30 / 79 /
359), SystemLib (101 / 94 / 34), Framework (90 / 18 / 14), SystemService (194 /
37 / 24), Application (83 / 271 / 25), in Android / Linux / HarmonyOS order.
`RuntimeVM` (2 / 1 / 44) fails the rule and is reported in the composition table
but excluded from inference, rather than pooled into an "other" category that
would hide the exclusion.

## Experiments

* **E1 — composition.**  Count and share per system and layer; pooled shares;
  support flag (`results/layer_composition.csv`).
* **E2 — within-layer.**  Full distributions of affected function and trigger
  scenario inside every layer, with `n` (`layer_within_*.csv`), plus per-layer
  pairwise JSD for the five shared layers (`layer_pairwise_*.csv`).
* **E3 — standardisation.**  Raw, pooled-standardised and uniform-standardised
  marginals; pairwise JSD for the three pairs and both dimensions
  (`layer_distances.csv`).
* **E4 — comparison.**  Raw vs standardised vs within-layer distances; the
  explained share; the two summary figures.

## Validation

* Three full runs of the analysis in separate directories; every generated file
  is hashed and the hashes are compared (`results/determinism.json`).  Identical
  output; the measured standard deviation of the reported values is 0.00 by
  construction.
* Unit tests cover the distance metric (identity, disjointness, symmetry), the
  composition percentages, the support rule, the `explained` arithmetic and the
  agreement between the generated table and a direct recount of the dataset
  (`tests/test_layer_rules.py`).
* The script reads only the pinned snapshot and fails loudly on unknown labels
  or malformed counts.

## Limitations

* The labels are the authors' own; the analysis inherits the labelling
  limitation of the whole replication and cannot test label reliability.
* Some within-layer cells are small (Framework 90/18/14, SystemService
  194/37/24, Application 83/271/25); their distances are indicative.
* Jensen–Shannon is dominated by the largest categories and is a distribution
  distance, not a causal test: the analysis quantifies how much of the
  difference is compositional, it does not explain why the layers differ.
* `RuntimeVM` cannot be compared at the 10-defect threshold.

## References

1. Zuo, Li, Jiang. *Toward Understanding Operating System Defects.*
   arXiv:2608.20643v1, 2026.  Table II, Tables III–V, Figure 4.
2. Author dashboard: <https://zuohongyao.github.io/> (pinned copy, 2026-11-05).
3. Group baseline: `../liuxin1240013249/` (data extraction, label vocabulary,
   paper transcription).
