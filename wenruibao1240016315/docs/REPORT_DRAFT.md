# Report draft — sections owned by the verification track

Draft text for the group report (English, ready to edit/merge).  Numbers are the
committed results in `../results/`; edit only if the dataset or the code changes.

---

## 3.3 Claim C3 — cross-system similarity is only partially supported

The paper compares the three systems with Spearman's rank correlation over
category vectors (Figure 4) and concludes that they are broadly dissimilar.  We
recomputed all twelve printed coefficients from the released dataset.  Panels
(a)–(c), nine coefficients, reproduce exactly.  Panel (d), the "overall"
heatmap, does not reproduce under any rule we tried (Section 3.4), and the
paper's own text contradicts its heatmap about that panel.

We therefore mark C3 **partially supported**: supported for the dimensions that
are printed as separate panels, not supported for the aggregate panel.  The
qualitative reading of Finding 5 — the systems differ — is consistent with
everything that does reproduce, and the metric-sensitivity experiment in
Section 3.5 shows that this part of the conclusion is robust.

*Evidence:* `results/fig4.csv`, `results/comparison.csv` (9/12 matches),
`docs/DISCREPANCIES.md`.

## 3.4 Figure 4d — the gap is a specification gap, not an implementation bug

The three printed coefficients of the "overall" panel are 0.05 (Android–Linux),
−0.11 (Android–HarmonyOS) and −0.04 (HarmonyOS–Linux).  Our recomputation gives
0.16, 0.08 and 0.05.

Two facts show that this is not an error on our side.

**Two independent implementations agree.**  The group's main implementation and
the verification-track implementation were written separately, share no source
file, and were compared value by value: 603/603 values and 591/591 underlying
defect counts are identical.  Both produce 0.16 / 0.08 / 0.05 for panel (d).
Any single-implementation bug would have to appear identically in two programs
written from the paper's definitions without shared code, which is implausible.

**No plausible construction reproduces the panel.**  The paper never states how
the overall vector is built.  We evaluated eight candidate rules: pooling panels
(a)–(c) or (a)–(e), with and without removing categories that are zero for both
systems, and averaging the per-panel coefficients either directly or through
Fisher's z.  The eight rules give Android–HarmonyOS values between 0.08 and
0.39, never negative, while the paper prints −0.11 (`results/fig4d_candidates.csv`).
In addition, the text discussing the panel attributes −0.11 to "Linux and
Android", whereas the heatmap places it on Android–HarmonyOS and prints 0.05 for
Android–Linux.

The panel is therefore under-specified and internally inconsistent.  We treat the
three coefficients as unreproducible until the authors state the rule or release
the analysis code, and we do not use them as evidence for or against the paper's
conclusion.

## 3.5 Extension — does the similarity conclusion depend on the metric?

Spearman's rho only sees the order of the categories: two systems that place
40 % and 80 % of their defects in the same category receive the same coefficient.
To test whether the paper's conclusion depends on that property, we kept the data
and the category sets fixed and changed one factor — the similarity measure — to
the Jensen–Shannon distance between the percentage distributions (0 = identical,
1 = disjoint support).  The experiment uses the same 500 defects per system and
the same label mapping as the main replication.

**Result.**  All twelve panel/pair comparisons stay far apart under the new
metric: JSD = 0.388–0.688 (Table 4).  The qualitative conclusion is therefore
robust: no pair of systems behaves alike, whether one compares ranks or
magnitudes.

The *ordering* of the three pairs is not robust.  Across the four panels, the
rank order of the pairs agrees between the two metrics in only 6 of 12
panel/pair slots, and the most similar pair differs in panels (c) and (d).  For
example, under Spearman the most similar pair for trigger scenarios is
HarmonyOS–Linux (0.41), whereas under Jensen–Shannon it is Android–HarmonyOS
(0.388 against 0.615).

**Interpretation.**  The paper's Finding 5 survives the change of measure at the
level of "the three systems differ", but claims of the form "A is more similar to
B than to C" depend on the metric and should be stated with it.  This is
consistent with C3 being only partially supported.

**Limitation.**  Jensen–Shannon compares the distributions as wholes and is
dominated by the largest categories; like Spearman it treats all categories as
equally important.  Neither measure tests whether the *labels* are reliable,
which remains the main limitation of the replication (Section 2).

*Evidence:* `scripts/extension.py`, `results/extension_jsd.csv`.

---

## Table for Section 3.5 (JSD by panel)

| Panel | Android–Linux | Android–HarmonyOS | HarmonyOS–Linux |
| --- | ---: | ---: | ---: |
| (a) OS layer | 0.464 | 0.688 | 0.611 |
| (b) affected function | 0.558 | 0.422 | 0.513 |
| (c) trigger scenario | 0.665 | 0.388 | 0.615 |
| (d) overall | 0.568 | 0.517 | 0.582 |

## Sentences that can go in the abstract / introduction

* "Two independently written implementations agree on all 603 recomputed values,
  so the reported numbers are a property of the dataset rather than of one code
  base."
* "Nine of the twelve Figure 4 coefficients reproduce exactly; the three that do
  not belong to an under-specified panel whose printed values also contradict
  the paper's text."
