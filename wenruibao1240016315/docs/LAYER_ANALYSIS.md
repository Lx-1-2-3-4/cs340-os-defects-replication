# Layer composition and cross-system differences

**Question.** The three systems differ in their overall defect distributions.
Part of that difference may simply come from *where* their defects live: the
samples have very different OS-layer mixes.  How much of the cross-system
difference is explained by that composition, and what remains once the layer mix
is held constant?

This is the analysis assigned to Wen Ruibao (1240016315) in the group's task
split.  Everything below is produced by `../scripts/layer_analysis.py` from the
same 1,500 released records used by the replication; the numbers can be
regenerated with `make layer`.

## Method

1. **Layer composition.**  For each system, count the 500 defects by `OS Layer`
   and express them as a share (`../results/layer_composition.csv`).
2. **Within-layer comparison.**  Inside each shared layer, compare the
   distributions of affected function and trigger scenario, with the layer's
   sample size attached (`layer_within_*.csv`, `layer_pairwise_*.csv`).
3. **Standardisation.**  Rebuild each system's marginal distribution as a
   weighted average of its within-layer distributions,
   `P_std(c) = Σ_l w_l · P(c | l)`, with two weight sets:
   * *pooled*: each layer's share of all 1,500 defects (the group's actual mix);
   * *uniform*: the five shared layers weighted equally.
4. **Distance comparison.**  Jensen–Shannon distance (base 2, 0 = identical,
   1 = disjoint support) between systems, for the raw marginals, the
   standardised marginals and the weighted average of within-layer distances
   (`layer_distances.csv`).  A negative "explained" value means the raw
   difference *understates* the difference inside layers.

**Support rule.**  A layer enters steps 2–4 only if it has at least 10 defects
in **all three** systems.  `RuntimeVM` fails this test (Android 2, Linux 1,
HarmonyOS 44) and is excluded; it is reported in the composition table but not
used for inference.

## Layer composition

| Layer | Android n (%) | Linux n (%) | HarmonyOS n (%) | Pooled share |
| --- | ---: | ---: | ---: | ---: |
| Kernel | 30 (6.0) | 79 (15.8) | 359 (71.8) | 31.2 % |
| SystemLib | 101 (20.2) | 94 (18.8) | 34 (6.8) | 15.3 % |
| RuntimeVM | 2 (0.4) | 1 (0.2) | 44 (8.8) | 3.1 % |
| Framework | 90 (18.0) | 18 (3.6) | 14 (2.8) | 8.1 % |
| SystemService | 194 (38.8) | 37 (7.4) | 24 (4.8) | 17.0 % |
| Application | 83 (16.6) | 271 (54.2) | 25 (5.0) | 25.3 % |

The mixes are close to disjoint in shape: HarmonyOS is a kernel-dominated
sample (71.8 %), Linux an application-layer sample (54.2 %), Android a
system-service sample (38.8 %).  Any marginal comparison across the three
therefore compares different layer populations as much as different systems.

Weights over the five shared layers: pooled Kernel 0.322, SystemLib 0.158,
Framework 0.084, SystemService 0.175, Application 0.261; uniform 0.200 each.

## Cross-system distances before and after adjustment

| Dimension | Pair | Raw | Standardised (pooled) | Standardised (uniform) | Within-layer average | Explained (pooled) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Affected function | Android–Linux | 0.557 | 0.559 | 0.554 | 0.654 | −0.2 % |
| Affected function | Android–HarmonyOS | 0.422 | **0.241** | 0.232 | 0.441 | **+43.0 %** |
| Affected function | Linux–HarmonyOS | 0.513 | 0.534 | 0.526 | 0.636 | −4.1 % |
| Trigger scenario | Android–Linux | 0.665 | 0.682 | 0.663 | 0.743 | −2.7 % |
| Trigger scenario | Android–HarmonyOS | 0.388 | **0.203** | 0.230 | 0.368 | **+47.8 %** |
| Trigger scenario | Linux–HarmonyOS | 0.615 | 0.653 | 0.631 | 0.723 | −6.1 % |

The pooled and uniform weights give the same picture (±3 percentage points), so
the conclusion does not depend on how the common weights are chosen.

## Within-layer distances

| Layer | Function: And–Lin | And–Har | Lin–Har | Trigger: And–Lin | And–Har | Lin–Har |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Kernel | 0.689 | 0.436 | 0.620 | 0.866 | **0.179** | 0.810 |
| SystemLib | 0.622 | 0.483 | 0.782 | 0.698 | 0.240 | 0.624 |
| Framework | 0.708 | 0.512 | 0.505 | 0.823 | 0.683 | 0.771 |
| SystemService | 0.624 | 0.368 | 0.613 | 0.621 | 0.319 | 0.741 |
| Application | 0.634 | 0.447 | 0.627 | 0.673 | 0.612 | 0.646 |

Sample sizes per layer: Kernel 30/79/359, SystemLib 101/94/34, Framework 90/18/14,
SystemService 194/37/24, Application 83/271/25 (Android/Linux/HarmonyOS).

## Findings

1. **Layer composition explains about half of the Android–HarmonyOS gap, and
   nothing of the Linux gaps.**  Standardising the layer mix reduces
   Android–HarmonyOS from 0.422 to 0.241 (affected function, −43 %) and from
   0.388 to 0.203 (trigger scenario, −48 %).  For Android–Linux and
   Linux–HarmonyOS the distance does not fall (it rises by 0.2–6.1 %), so their
   differences are not compositional.

2. **For the Linux pairs the raw comparison understates the difference.**  The
   weighted average of within-layer distances is larger than the raw distance
   (function: 0.654 vs 0.557 for Android–Linux, 0.636 vs 0.513 for
   Linux–HarmonyOS).  This is a Simpson-type effect: because the three systems
   draw their defects from different layers, the marginal distributions look
   more alike than the systems do inside the same layer.

3. **Inside the shared layers, Linux is the outlier.**  Kernel trigger scenario:
   Android–HarmonyOS 0.179 but Linux–HarmonyOS 0.810 and Android–Linux 0.866.
   SystemLib trigger scenario: 0.240 against 0.624 and 0.698.  The Android and
   HarmonyOS labelling conventions are much closer to each other than either is
   to Linux, in every layer with enough data.

4. **The "the systems differ" conclusion survives the adjustment.**  After
   controlling for layer mix, every pair is still far apart (0.203–0.682), and
   no pair becomes similar (< 0.2).  What changes is the *ranking* of pairs:
   raw distances put Android–HarmonyOS as the closest pair in the trigger
   dimension, and it remains the closest after adjustment, but the gap to the
   other pairs widens.

5. **Small cells limit the per-layer claims.**  Framework, SystemService and
   Application have 14–37 defects on the HarmonyOS or Linux side; their
   within-layer distances are reported with n and should be read as indicative,
   not precise.

## What this means for the paper

The paper reports marginal distributions (Table II) and joint tables
(Tables III–V) but never controls for the layer mix when comparing systems.
This analysis shows the missing control matters in a specific, asymmetric way:
it inflates the apparent Android–HarmonyOS difference (about half of which is
composition) and masks part of the Linux-related differences.  The paper's
qualitative conclusion is not overturned — the systems still differ after
adjustment — but any quantitative statement of the form "system A is X % more
like B" needs the layer mix held fixed.

## Report-ready text (English)

> The three samples are not drawn from comparable layer populations: 71.8 % of
> the HarmonyOS defects are in the kernel layer against 15.8 % for Linux and
> 6.0 % for Android, while Linux is dominated by application-layer defects
> (54.2 %) and Android by system-service defects (38.8 %).  To test whether the
> cross-system differences survive this imbalance we standardised each system to
> the pooled layer mix and to a uniform mix over the five shared layers.  Layer
> composition accounts for roughly half of the Android–HarmonyOS difference
> (Jensen–Shannon distance 0.422 → 0.241 for affected functions and 0.388 → 0.203
> for trigger scenarios, −43 % and −48 %).  For the two pairs involving Linux the
> standardised distance does not decrease; the weighted average of within-layer
> distances is in fact larger than the raw distance (0.654 vs 0.557 and 0.636 vs
> 0.513 for affected functions), a Simpson-type effect in which the layer mix
> masks differences that are present inside every shared layer.  The conclusion
> that the three systems behave differently therefore holds after the control,
> but the size and ordering of the pairwise differences are composition-sensitive.

## Files

| File | Content |
| --- | --- |
| `../scripts/layer_analysis.py` | the whole analysis (composition, within-layer, standardisation, figures) |
| `../results/layer_composition.csv` | system × layer counts, shares, pooled shares, support flag |
| `../results/layer_within_function.csv`, `layer_within_trigger.csv` | within-layer distributions with n |
| `../results/layer_pairwise_function.csv`, `layer_pairwise_trigger.csv` | per-layer pairwise JSD with n |
| `../results/layer_distances.csv` | raw / standardised / within-layer distances and explained share |
| `../figures/layer_composition.png` | layer composition of the three samples |
| `../figures/layer_distance_adjustment.png` | distances before and after adjustment |
