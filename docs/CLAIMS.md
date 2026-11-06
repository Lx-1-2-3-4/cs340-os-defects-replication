# Claims, scope and verdicts

Paper: *Toward Understanding Operating System Defects*, Hongyao Zuo, Jiali Li,
Jiajun Jiang, arXiv:2608.20643v1 (2026).

## Scope

All 1,500 released defect records are used (500 each for Android, Linux and
HarmonyOS). We recompute every quantitative value in Table II (five panels),
Tables III–V (three joint tables), Figures 2–3 (change size distributions) and
Figure 4 (cross-OS similarity), 603 values in total.

Not covered:

- the manual labelling of the 1,500 patches (two annotators, Cohen's kappa
  0.8–1.0);
- the collection funnel of Table I (32,249 Linux / 1,750 Android / 712 HarmonyOS
  initial reports);
- the qualitative taxonomy of Figure 1 and the paper's discussion sections.

The authors released the labelled records but not the raw candidate pool or the
annotation protocol. The reproduction therefore covers the analysis, not the
measurement; this is also recorded as deviations D1–D2 in
[`DEVIATIONS.md`](DEVIATIONS.md).

Because the input labels are the authors' own, exact matches on Table II mean the
mapping and aggregation are right. They say nothing about whether the labels are
right. The result worth attention is the one that does not match, Figure 4d, and
the inconsistency between the paper's text and that heatmap.

## C1. The five defect distributions differ across systems (Table II, Finding 1)

Table II, all five panels, quoted in Section IV-A. Metric: percentage of the 500
defects per system in each category. We check all 114 percentages, including the
top categories (Android System Service Layer 38.80%, Linux Application Layer
54.20%, HarmonyOS Kernel Layer 71.80%).

Verdict: supported. 114/114 values match
(`results/table2_reproduction.csv`).

## C2. Joint distributions reveal system-specific relationships between dimensions (Tables III–V, RQ2)

Table III (OS layer × affected function), Table IV (OS layer × trigger scenario),
Table V (affected function × trigger scenario). Metric: percentage of defects in
each joint cell. We check 438 joint percentages.

Verdict: supported. 438/438 values match (`results/table3_reproduction.csv`,
`table4_reproduction.csv`, `table5_reproduction.csv`).

## C3. Cross-OS defect distributions are compared by Spearman's rho (Figure 4, Finding 5)

Figure 4, panels (a) OS layer, (b) affected function, (c) trigger scenario,
(d) overall; Section IV-C. Metric: Spearman rank correlation between the category
vectors of each OS pair. We check the 12 printed coefficients.

Verdict: partially supported. Panels (a)–(c) reproduce exactly, 9/9 coefficients.
Panel (d) does not reproduce under any of the five aggregation rules we tried, and
the paper's text attributes the −0.11 coefficient to a different OS pair than the
heatmap does. See [`DISCREPANCIES.md`](DISCREPANCIES.md).

The qualitative part of Finding 5, that the systems are broadly dissimilar, is
consistent with our recomputation: the coefficients produced by the candidate
rules lie between −0.01 and 0.39, so no candidate supports a strong positive
relationship. The exact printed panel-(d) matrix cannot be reproduced from the
released dataset without knowing how the panel was built.

## C4. Repairs are small-scale and touch few functions/files (Figures 2–3)

Figure 2 (changed code lines) and Figure 3 (involved functions and modified
files), quoted in Section IV-A5. Metric: percentage of defects per histogram
bucket. We check 15 Figure 2 percentages and 24 Figure 3 percentages.

Verdict: supported. 39/39 values match (`results/fig2_reproduction.csv`,
`results/fig3_reproduction.csv`).

## Overall

600 of the 603 paper values (99.50%) recompute exactly from the released
dataset. The three exceptions are the under-specified Figure 4d "Overall" panel,
and the paper is internally inconsistent about that panel. C1, C2 and C4 are
supported; C3 is only partly supported, in its qualitative form.
