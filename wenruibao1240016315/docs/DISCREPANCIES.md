# Figure 4 panel (d): the one result that does not reproduce

Panels (a)–(c) of Figure 4 reproduce exactly (9/9 coefficients).  Panel (d),
the “overall” heatmap, does not:

| Pair | Paper (heatmap) | Ours |
| --- | ---: | ---: |
| Android–Linux | 0.05 | 0.16 |
| Android–HarmonyOS | −0.11 | 0.08 |
| HarmonyOS–Linux | −0.04 | 0.05 |

The paper does not describe how the overall vector is built.  To show that the
gap is a specification gap rather than a coding error, `scripts/fig4d_candidates.py`
evaluates eight plausible constructions on the same data:

| Rule | Android–Linux | Android–HarmonyOS | HarmonyOS–Linux | Matches |
| --- | ---: | ---: | ---: | --- |
| pool panels (a)–(c), drop shared zeros (baseline) | 0.16 | 0.08 | 0.05 | 0/3 |
| pool panels (a)–(c), keep zeros | 0.16 | 0.21 | 0.05 | 0/3 |
| pool panels (a)–(e), drop shared zeros | 0.35 | 0.35 | 0.34 | 0/3 |
| pool panels (a)–(e), keep zeros | 0.35 | 0.39 | 0.34 | 0/3 |
| mean of the panel coefficients (a)–(c) | 0.09 | 0.13 | −0.01 | 0/3 |
| Fisher-z mean of the panel coefficients (a)–(c) | 0.10 | 0.13 | −0.02 | 0/3 |
| mean of the panel coefficients (a)–(e) | 0.25 | 0.22 | 0.14 | 0/3 |
| Fisher-z mean of the panel coefficients (a)–(e) | 0.33 | 0.32 | 0.26 | 0/3 |

No rule reproduces the printed values.  Across the eight rules the
Android–HarmonyOS coefficient ranges from 0.08 to 0.39 and never becomes
negative, while the paper prints −0.11.  The rules that pool all five panels
(a)–(e) give fairly *high* correlations (0.32–0.39), which is the opposite of
the “broadly dissimilar” reading of the figure.

## The paper is also internally inconsistent here

The text discussing panel (d) states that the largest absolute coefficient,
−0.11, is “between Linux and Android”, but the heatmap places −0.11 on the
Android–HarmonyOS cell and prints 0.05 for Android–Linux.  The transcription in
`data/paper/fig4.csv` follows the heatmap, which is what this replication
compares against.

## What this means for the claim

The numeric claim of panel (d) cannot be verified from the released data: the
construction rule is missing and the paper contradicts itself.  Two things can
still be said:

1. The *qualitative* claim of Finding 5 — the systems differ — is consistent with
   everything that does reproduce: panels (a)–(c) are small or negative under
   Spearman, and the magnitude-sensitive Jensen–Shannon distances in the
   extension are 0.39–0.69 (see `docs/CLAIMS.md`, C5).
2. The specific coefficients of panel (d) should be treated as unreproducible
   until the authors state the rule (or release the analysis code).

This is why claim C3 is marked “partially supported” rather than “not supported”:
the reproducible part of the finding holds, the panel-(d) numbers do not.
