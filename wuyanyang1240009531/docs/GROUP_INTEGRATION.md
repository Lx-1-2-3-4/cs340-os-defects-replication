# Integration into the group submission

This module is a member supplement. Preserve the group's existing numerical
baseline and bootstrap/JSD contributions with their original attribution.

## Fit within three main claims

| Group claim | This module supplies | Existing work still needed |
| --- | --- | --- |
| C1: descriptive defect composition differs across OS samples | Input consistency checks and limitations of published labels | Baseline Table II, distribution charts and denominator definitions |
| C2: selected repairs concentrate in smaller size bins | 39 half-open comparisons; endpoint sensitivity; zero/censored-value treatment | Main Figure 2–3 visual reproduction and selection-scope discussion |
| C3: cross-OS similarity depends on dimension; Overall is unresolved | Nine rho policy contrasts, category vectors, strength change | Existing Figure 4 baseline, bootstrap extension, explicit 4d discrepancy |

Do not promote every sensitivity experiment to a fourth/fifth author claim.
The group may retain the existing Figure 4 bootstrap as its main extension and
present this module as preprocessing robustness/discrepancy evidence. The two
contrasts here change one factor at a time; they must not be merged into a
single experiment that changes both zero handling and endpoints simultaneously.

## Suggested report material

1. Methods: snapshot/version, category alignment, inferred versus explicit
   author rules, three-process repeatability protocol.
2. Results/discrepancies: `paper_vs_ours.csv`, rho 0.613 versus 0.377, and the
   endpoint table/chart with units and denominator 500 per OS.
3. Limitations: all same-data reconstructions; no re-annotation; bounded `10+`
   cells; repeat-run SD differs from bootstrap and identification bounds;
   most-frequent bin differs from a majority; selection cap limits external
   generalization.
4. Contribution and AI assistance: use the actual member and tool disclosure,
   adding human review only after it occurs.

## Remaining group-level requirements

The course handout requires an English final group PDF, focused claims,
Paper-vs-Ours evidence, repeated runs with mean/SD, traceable logs, charts,
one-factor extension and explanation of discrepancies. This HTML/Markdown
supplement and its 57-row table help meet these; they do not replace the whole
group report or count as a completed final submission.

Before final submission, consolidate the group's main figures and results,
resolve report terminology, retain the Figure 4(d) non-reproduction, obtain an
independent teammate's clean-environment run, and execute Docker/remote CI for
real where required. Presentation instructions must be checked separately.

The handout's weekly substantive push deadline is Sunday 23:59. The
**15 November 2026, 23:59** check is in the past as of 16 November 2026;
the next Sunday is **22 November 2026**, subject to the course's timezone and
instructions. Local files do not count as a push. User
approval is still required before uploading this work. Commit messages must
include `1240009531 吴彦阳`; do not fabricate or backdate history. The final
`v1.0` tag belongs to the actual final group release, not this local draft.
