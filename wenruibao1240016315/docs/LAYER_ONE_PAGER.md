# Layer composition and cross-system differences — one-page summary

**Wen Ruibao (1240016315) · CS340 replication of arXiv:2608.20643v1 · 2026-11-26**

## 1. What we test

The paper compares Android, Linux and HarmonyOS on the whole set of 500 defects
per system and reports that their distributions differ.  The three samples,
however, are not drawn from comparable layer populations: 71.8 % of the
HarmonyOS defects are in the kernel layer against 15.8 % for Linux and 6.0 % for
Android, while Linux is dominated by application-layer defects (54.2 %) and
Android by system-service defects (38.8 %).  We test whether the reported
cross-system differences in affected function and trigger scenario are partly a
consequence of that composition, and how much difference remains once the layer
mix is held constant.

## 2. How the control is set

* Data: the same 1,500 released defect records used by the replication; no new
  labelling.
* Support rule: a layer enters the comparison only if it has at least 10 defects
  in **all three** systems.  Five layers qualify (Kernel, SystemLib, Framework,
  SystemService, Application); `RuntimeVM` (2 / 1 / 44) is reported in the
  composition table but excluded from inference.
* Within-layer comparison: affected-function and trigger-scenario distributions
  are compared inside each shared layer, with the layer sample size attached.
* Standardisation: each system's marginal is rebuilt as
  `P_std(c) = Σ_l w_l · P(c | l)` under two weight sets — *pooled* (each layer's
  share of all 1,500 defects: Kernel 0.322, SystemLib 0.158, Framework 0.084,
  SystemService 0.175, Application 0.261) and *uniform* (0.200 each).
* Distance: Jensen–Shannon distance (base 2, 0 = identical, 1 = disjoint
  support), reported for the raw marginals, the standardised marginals and the
  weighted average of within-layer distances.

## 3. What we observe

| Dimension | Pair | Raw | Standardised (pooled) | Change |
| --- | --- | ---: | ---: | ---: |
| Affected function | Android–Linux | 0.557 | 0.559 | −0.2 % |
| Affected function | Android–HarmonyOS | 0.422 | **0.241** | **−43.0 %** |
| Affected function | Linux–HarmonyOS | 0.513 | 0.534 | +4.1 % |
| Trigger scenario | Android–Linux | 0.665 | 0.682 | −2.7 % |
| Trigger scenario | Android–HarmonyOS | 0.388 | **0.203** | **−47.8 %** |
| Trigger scenario | Linux–HarmonyOS | 0.615 | 0.653 | −6.1 % |

The uniform weights give the same picture (within ±3 percentage points), so the
result does not depend on the choice of common mix.

Three observations stand out.

1. **Composition explains about half of the Android–HarmonyOS gap, and none of
   the Linux gaps.**  Standardising the layer mix cuts the Android–HarmonyOS
   distance by 43 % (function) and 48 % (trigger), but leaves the two
   Linux-involving pairs unchanged or slightly larger.
2. **For the Linux pairs the raw comparison understates the difference.**  The
   weighted average of within-layer distances is larger than the raw distance
   (function: 0.654 vs 0.557 for Android–Linux and 0.636 vs 0.513 for
   Linux–HarmonyOS) — a Simpson-type effect in which the layer mix masks
   differences that are present inside every shared layer.
3. **Inside the shared layers, Linux is the outlier.**  Kernel trigger scenario:
   Android–HarmonyOS 0.179, but Linux–HarmonyOS 0.810 and Android–Linux 0.866;
   SystemLib trigger scenario: 0.240 against 0.624 and 0.698.

## 4. What this means for the paper

The conclusion that the three systems behave differently survives the control:
after adjusting for layer mix every pair is still far apart (0.203–0.682) and no
pair becomes similar.  What does not survive is any quantitative statement about
the *size* or *ordering* of the pairwise differences as if it were a property of
the systems: for Android–HarmonyOS roughly half of the reported gap is
composition, and for the Linux pairs the reported gap is conservative.  The
paper reports marginal distributions and joint tables but never controls for the
layer mix when comparing systems; this analysis shows that the control matters,
in opposite directions for different pairs.

## 5. Reused vs new

**Reused from the group's existing results:** the 1,500-record dataset and its
provenance, the label mapping, the OS-layer/function/trigger categories, and the
distribution definitions of Table II.

**New in this round:** the layer-composition table, the within-layer comparisons
with sample sizes, the standardisation under two weight sets, the before/after
distance decomposition, the two figures, and the finding that the effect is
asymmetric across pairs.

## 6. Limitations

* The labels are the authors' own; this analysis inherits the labelling
  limitation of the whole replication.
* Several within-layer cells are small (Framework 90/18/14, SystemService
  194/37/24, Application 83/271/25); their distances carry n and are indicative.
* `RuntimeVM` cannot be compared and is excluded rather than pooled into
  "other", to avoid hiding the exclusion.
* Jensen–Shannon is dominated by the largest categories; it is a distribution
  distance, not a causal test.  The analysis quantifies composition, it does not
  prove why the layers differ.

*Deliverables:* `layer_analysis.py` (analysis), `results/layer_*.csv` (six
tables), `figures/layer_composition.png` and `figures/layer_distance_adjustment.png`,
and the full write-up in `LAYER_ANALYSIS.md`.
