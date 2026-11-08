# Claims, scope and verdicts

Paper: *Toward Understanding Operating System Defects*, Hongyao Zuo, Jiali Li,
Jiajun Jiang, arXiv:2608.20643v1 (2026).

## Scope

All 1,500 released defect records (500 each for Android, Linux and HarmonyOS)
are used.  We recompute every quantitative value the paper prints: the five
panels of Table II, the joint tables III–V, the change-size histograms of
Figures 2–3 and the cross-system Spearman coefficients of Figure 4 — 603 values
in total.

Not covered:

* the manual labelling of the 1,500 patches (two annotators, Cohen's kappa
  0.8–1.0) and the collection funnel of Table I;
* the qualitative taxonomy of Figure 1 and the discussion sections, which are
  not numeric.

Because the released file carries the authors' labels, exact agreement on
Tables II–V means our mapping and aggregation are right; it says nothing about
whether the labels are right.  The one value family that does not reproduce
(Figure 4d) is discussed in `DISCREPANCIES.md`.

## C1 — The defect distributions differ across the three systems (Table II)

Metric: percentage of the 500 defects of each system in every category, five
panels (OS layer, affected function, trigger scenario, severity, repaired code
element).

Verdict: **supported**.  114/114 values match, including the headline
categories (Android SystemService 38.80 %, Linux Application 54.20 %, HarmonyOS
Kernel 71.80 %).  See `results/table2.csv` and `results/comparison.csv`.

## C2 — Joint distributions reveal system-specific relations between dimensions (Tables III–V)

Metric: percentage of the 500 defects of each system in each joint cell of
OS layer × affected function (Table III), OS layer × trigger scenario (Table
IV) and affected function × trigger scenario (Table V).

Verdict: **supported**.  438/438 joint percentages match
(`results/table3.csv`, `table4.csv`, `table5.csv`).

## C3 — Cross-system similarity measured by Spearman's rho (Figure 4)

Metric: Spearman rank correlation between the category vectors of each pair of
systems, for the four panels printed in the heatmaps.

Verdict: **partially supported**.  Panels (a)–(c) reproduce exactly, 9/9
coefficients.  Panel (d), “overall”, does not reproduce under any of the eight
rules we tried, and the paper's text and heatmap disagree about which pair the
−0.11 coefficient belongs to (`DISCREPANCIES.md`).  The qualitative part of the
finding — that the systems differ substantially — is consistent with the
recomputation: all panel coefficients that do reproduce are small or negative,
and the magnitude-sensitive check in C5 gives distances of 0.39–0.69.

## C4 — Repairs are small: few changed lines, few functions and files (Figures 2–3)

Metric: percentage of defects per histogram bucket of changed code lines
(Figure 2) and of involved functions / modified files (Figure 3).

Verdict: **supported**.  39/39 percentages match (`results/fig2.csv`,
`results/fig3.csv`).  The bucket boundaries are half-open intervals, inferred
from the printed labels; they reproduce all 39 values exactly (deviation D7).

## C5 (extension) — Is the similarity conclusion metric-dependent?

Question: Spearman's rho only sees the order of the categories; two systems
that put 40 % and 80 % of their defects in the same category get the same
coefficient.  Does the paper's “the systems are dissimilar” conclusion survive a
metric that also looks at magnitudes — the Jensen–Shannon distance between the
percentage distributions?

Design: same data, same category sets, one factor changed (the similarity
measure).  `scripts/extension.py`.

Result: **the qualitative conclusion is robust, the ordering is not.**  All
twelve panel/pair comparisons stay far apart under both metrics (JSD
0.388–0.688, where 0 means identical distributions and 1 means disjoint
support), so “no two systems behave alike” does not depend on the metric.  But
the three pairs change rank in 6 of the 12 panel/pair slots, and the most
similar pair differs in panels (c) and (d).  Statements of the form “A is more
similar to B than to C” should therefore be made with the metric stated.

## Overall

600 of 603 printed values (99.50 %) recompute exactly from the released
dataset.  The three exceptions are the three coefficients of the under-specified
Figure 4d panel, which is also internally inconsistent in the paper.  C1, C2 and
C4 are supported; C3 is supported only for panels (a)–(c); the extension (C5)
shows that the dissimilarity conclusion is robust to the choice of similarity
measure.
