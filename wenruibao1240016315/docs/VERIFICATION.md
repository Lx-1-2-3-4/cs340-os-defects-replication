# What this implementation verified

This page records what the second implementation checked and what it found.  The
wording of the claims and the verdicts used in the group report are maintained
in `../../liuxin1240013249/docs/CLAIMS.md`; they are not repeated here, to keep
one authoritative copy.

## Result in one table

| Claim (paper item) | Values | Paper match | Main implementation match |
| --- | ---: | ---: | ---: |
| C1 — five defect distributions differ across systems (Table II) | 114 | 114 | 114 |
| C2 — joint distributions are system-specific (Tables III–V) | 438 | 438 | 438 |
| C3 — cross-system similarity by Spearman's rho (Figure 4) | 12 | 9 | 12 |
| C4 — repairs are small (Figures 2–3) | 39 | 39 | 39 |
| **Total** | **603** | **600** | **603** |

The 591 defect counts behind the percentages also match the main implementation
exactly (the six Figure 4 coefficients have no count).

## What the cross-check adds

The main implementation and this one share no source file: the data loading,
label mapping, aggregation and rank correlation are written independently.  They
agree on every one of the 603 values.  Two consequences:

* The 600 matches with the paper are a property of the dataset, not of a lucky
  implementation.
* The three Figure 4d values that differ from the paper are computed identically
  by both implementations (0.16 / 0.08 / 0.05).  The gap is therefore in the
  paper's under-specified panel, not in either program.  This is the strongest
  single piece of evidence in the Figure 4 discussion.

## C5 — the extension owned by this track

**Question.** Spearman's rho is rank-based: two systems that put 40 % and 80 %
of their defects in the same category receive the same coefficient.  Does the
paper's "the systems are dissimilar" conclusion depend on that choice?

**Design.** Same data, same category sets, one factor changed: the similarity
measure becomes the Jensen–Shannon distance between the percentage
distributions (0 = identical, 1 = disjoint support).  Implemented in
`../scripts/extension.py`, results in `../results/extension_jsd.csv`.

**Result.** All twelve panel/pair comparisons stay far apart under both metrics
(JSD 0.388–0.688), so the qualitative conclusion is robust.  The ordering of the
three pairs changes in 6 of the 12 panel/pair slots, and the most similar pair
differs in panels (c) and (d).  Statements of the form "A is closer to B than to
C" therefore need the metric named.

**Interpretation for the report.** The paper's Finding 5 survives a change of
measure at the level of "the systems differ", but not at the level of "which
pair is closest".  This is consistent with C3 being only partially supported.
