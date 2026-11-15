# Figure 4 panel (d): an under-specified panel, not an implementation bug

Panels (a)–(c) of Figure 4 reproduce exactly.  Panel (d), the “overall” heatmap,
does not:

| Pair | Paper (heatmap) | This implementation | Main implementation |
| --- | ---: | ---: | ---: |
| Android–Linux | 0.05 | 0.16 | 0.16 |
| Android–HarmonyOS | −0.11 | 0.08 | 0.08 |
| HarmonyOS–Linux | −0.04 | 0.05 | 0.05 |

Two independent implementations produce the same three values, so the gap is not
a coding error on either side.

## The paper does not say how the panel is built

`scripts/fig4d_candidates.py` evaluates eight plausible constructions on the
same data:

| Rule | Android–Linux | Android–HarmonyOS | HarmonyOS–Linux | Matches |
| --- | ---: | ---: | ---: | --- |
| pool (a)–(c), drop shared zeros (baseline) | 0.16 | 0.08 | 0.05 | 0/3 |
| pool (a)–(c), keep zeros | 0.16 | 0.21 | 0.05 | 0/3 |
| pool (a)–(e), drop shared zeros | 0.35 | 0.35 | 0.34 | 0/3 |
| pool (a)–(e), keep zeros | 0.35 | 0.39 | 0.34 | 0/3 |
| mean of panel coefficients (a)–(c) | 0.09 | 0.13 | −0.01 | 0/3 |
| Fisher-z mean of panel coefficients (a)–(c) | 0.10 | 0.13 | −0.02 | 0/3 |
| mean of panel coefficients (a)–(e) | 0.25 | 0.22 | 0.14 | 0/3 |
| Fisher-z mean of panel coefficients (a)–(e) | 0.33 | 0.32 | 0.26 | 0/3 |

Across the eight rules the Android–HarmonyOS coefficient ranges from 0.08 to
0.39 and never becomes negative, while the paper prints −0.11.  The rules that
pool all five dimensions give fairly *high* correlations (0.32–0.39), the
opposite of a “broadly dissimilar” reading.

## The paper also contradicts itself

The text discussing panel (d) attributes the largest absolute coefficient, −0.11,
to “Linux and Android”, while the heatmap places −0.11 on the
Android–HarmonyOS cell and prints 0.05 for Android–Linux.

## What can still be concluded

1. The qualitative part of Finding 5 — the systems differ — is consistent with
   everything that reproduces: panels (a)–(c) are small or negative under
   Spearman, and the Jensen–Shannon distances in the extension are 0.39–0.69.
2. The three printed coefficients of panel (d) are not reproducible from the
   released data without knowing the aggregation rule.

For the group report this is the evidence behind the “partially supported”
verdict on C3.
