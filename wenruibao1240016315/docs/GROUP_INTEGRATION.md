# Group report integration

How this module plugs into the group's final report and presentation.

## Where it belongs

The analysis supports two places in the report:

1. **Results / Analysis of discrepancies**, as a robustness check on C1 and C2:
   the paper's Table II and Tables III–V report marginal and joint
   distributions without controlling for the layer mix.  The layer analysis shows
   the control matters and in which direction.
2. **Extension**, as the group's second extension (together with the
   missing-severity-label experiment): one factor changed — the layer mix — with
   the same data, labels and definitions.

It needs roughly one page: one paragraph of method, one distance table, the two
figures, one paragraph of interpretation.

## Suggested placement of the text

| Report element | Source here |
| --- | --- |
| Method paragraph | `LAYER_ONE_PAGER.md` §2 (prose version in `METHODS.md`) |
| Results table | `results/layer_distances.csv`, or the table in `LAYER_ANALYSIS.md` |
| Figure 1 (composition) | `figures/layer_composition.png` / `.svg` |
| Figure 2 (before/after) | `figures/layer_distance_adjustment.png` / `.svg` |
| Interpretation | `LAYER_ANALYSIS.md` §Findings, or `LAYER_ONE_PAGER.md` §4 |
| Limitations | `METHODS.md` §Limitations |

## Claim mapping

| Claim | How this module bears on it |
| --- | --- |
| C1 — distributions differ (Table II) | The differences are real but partially compositional: layer mix explains ~43–48 % of the Android–HarmonyOS gap and none of the Linux gaps |
| C2 — joint distributions are system-specific (Tables III–V) | Consistent: inside each shared layer the systems still differ, and for the Linux pairs the within-layer difference is larger than the marginal one |
| C3 — similarity (Figure 4) | Not directly; the layer analysis is independent of the correlation panel. Do not merge the two verdicts |
| Overall verdict | "Partially reproduced with a composition caveat": the qualitative conclusion holds after the control, the quantitative pairwise ordering is composition-sensitive |

## What the group should **not** claim from this module

* That layer composition *causes* the differences.  Standardisation is a
  statistical adjustment, not a causal identification.
* That the paper is wrong about Table II.  All Table II values still reproduce;
  the module only adds the control the paper does not perform.
* That the within-layer distances for small cells are precise.  They carry `n`
  and belong to a sensitivity discussion, not to a headline number.

## Reused vs new (for the report's provenance paragraph)

**Reused:** the 1,500 released records and their provenance, the label
vocabulary and mapping, the category definitions and Table II's denominator, the
main implementation's results for the replication numbers.

**New:** the layer-composition table, within-layer comparisons with sample
sizes, standardisation under pooled and uniform weights, the before/after
distance decomposition, both figures, the three-run determinism receipt and the
unit tests.

## Presentation

One slide is enough: the composition bar chart, the before/after distance chart,
and the sentence "composition explains about half of the Android–HarmonyOS gap,
and none of the Linux gaps — where it actually masks differences".  See
`SLIDES.md` for the verification-track slides; this module can replace or
precede its third slide.
