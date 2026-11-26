# Deviations and explicit settings

The paper does not control for layer composition, so every choice below is new
relative to the paper.  The table records what was chosen and why, in the format
the group's report requires (item, paper's setting, setting used, reason).

| ID | Item | Paper's setting | Setting used here | Reason |
| --- | --- | --- | --- | --- |
| L1 | Layer control | Not performed; systems are compared on the full 500-defect samples | Direct standardisation to a common layer mix, plus within-layer comparison | The layer mixes differ strongly (Kernel 6.0 / 15.8 / 71.8 %), so marginal comparisons mix system and layer effects |
| L2 | Minimum support | Not applicable | A layer is compared only if it has ≥ 10 defects in all three systems | Below 10 the within-layer distribution is estimated from a handful of defects; the rule is stated before looking at the results |
| L3 | RuntimeVM | Reported in Table II as a layer | Reported in the composition table, excluded from inference | 2 / 1 / 44 defects: it passes the threshold in one system only. Not merged into "other", so the exclusion stays visible |
| L4 | Common weights | Not specified | Two sets: pooled (each layer's share of all 1,500) and uniform (equal over the five shared layers) | The paper gives no target population; reporting both shows the result is not an artefact of one weighting choice |
| L5 | Distance | Spearman's rho in Figure 4 (rank-based) | Jensen–Shannon distance (base 2) between percentage distributions | Composition changes the marginal magnitudes; a magnitude-sensitive, bounded distance is the right tool for the before/after comparison. Spearman is still used by the baseline and is not replaced there |
| L6 | Labels | Authors' labels, two annotators, kappa 0.8–1.0 | Authors' released labels, unchanged | The candidate pool and annotation protocol are not public; re-labelling 1,500 patches is out of scope |
| L7 | Repeated runs | Single deterministic analysis | Three full runs, every output hashed; values identical, SD = 0.00 | The section requires ≥ 3 runs; the pipeline has no randomness, so the SD is 0 by construction and demonstrated, not asserted |
| L8 | Small cells | Not discussed | Reported with their `n` and not interpreted as precise | Framework, SystemService and Application have 14–37 defects on one side |
| L9 | Scale | 1,500 defects, three systems | Same 1,500 defects, no sampling | The comparison only needs the released records |

## What is deliberately *not* claimed

* The standardised differences are not causal: they hold the layer mix fixed
  statistically, they do not identify why each system has its own mix.
* The within-layer distances for small cells are not significance tests; no
  p-values are reported, because the sample is the full released set rather than
  a random draw from a defined population.
* `RuntimeVM` is not characterised; the exclusion is a sample-size decision, not
  a statement that the layer is unimportant.
