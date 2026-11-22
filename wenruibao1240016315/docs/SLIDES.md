# Slides draft — verification track (2–3 slides)

For the group presentation (2026-12-01).  Speaker notes are the text below each
slide; the numbers are from `../results/`.

---

## Slide 1 — "Two implementations, one answer"

**On the slide**

* Second, independent implementation: same 603 values, no shared source file
* Agreement with the main implementation: **603/603 values**, **591/591 defect
  counts**
* Paper values reproduced: **600/603** (99.50 %)

**Speaker notes (≈40 s)**

We did not just rerun the pipeline: a second implementation was written from the
paper's definitions, without sharing code with the main one.  It produces the
same 603 values and the same defect counts.  Against the paper, 600 of 603 values
match exactly — the three exceptions are all in one figure panel, and that is the
next slide.

---

## Slide 2 — "The one mismatch is in the paper, not the code"

**On the slide**

| Figure 4d pair | Paper | Ours (both implementations) |
| --- | ---: | ---: |
| Android–Linux | 0.05 | 0.16 |
| Android–HarmonyOS | −0.11 | 0.08 |
| HarmonyOS–Linux | −0.04 | 0.05 |

* 8 candidate rules tested → none reproduces the panel
* Paper text puts −0.11 on "Linux and Android"; its heatmap puts it on Android–HarmonyOS
* Verdict on C3: **partially supported**

**Speaker notes (≈60 s)**

Panel (d) of Figure 4 is the only place where the numbers do not match.  Both
implementations compute the same three coefficients, so it is not a coding error.
The paper never says how the "overall" vector is built; we tried eight plausible
constructions, and the Android–HarmonyOS value never goes negative — it ranges
from 0.08 to 0.39 while the paper prints −0.11.  On top of that, the text and the
heatmap disagree about which pair owns the −0.11.  So we call C3 partially
supported: the separate panels reproduce, the aggregate panel does not.

---

## Slide 3 — "Does the conclusion survive a different metric?"

**On the slide**

* Spearman's rho ignores magnitudes → repeat with Jensen–Shannon distance
* All 12 panel/pair distances far apart: **JSD 0.388–0.688**
* "The systems differ" → robust
* Pair *ordering* changes in **6/12** slots → metric-dependent

**Speaker notes (≈50 s)**

Spearman only sees the order of categories, so we repeated the comparison with a
measure that also sees magnitudes.  The systems stay far apart under both
metrics — the qualitative conclusion holds.  But which pair is "most similar"
changes depending on the metric, so the report should not make fine-grained
ordering claims without naming the measure.  That is the extension we contribute.

---

## Anticipated questions

**Q: If two implementations agree, isn't that just the same analysis twice?**
A: They share no code and were written from the paper's definitions separately.
Agreement rules out implementation bugs; it does not rule out mistakes in the
paper's own labels, which we cannot check (the annotations are not released).

**Q: Why not just report the paper is wrong on Figure 4d?**
A: Because the panel is under-specified, not demonstrably wrong.  The honest
verdict is "unreproducible without the rule", which is what we report.

**Q: Which extension should the report keep?**
A: The group decided to keep two: the missing-severity-label experiment (main
implementation) and this metric-sensitivity experiment, because they support
different claims (C1/C2 and C3 respectively).
