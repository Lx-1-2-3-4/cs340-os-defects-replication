# Methods: fixed-snapshot preprocessing sensitivity

## Research scope and provenance

Question: with the published labelled defect records fixed, do plausible
preprocessing conventions change numerical agreement and interpretation?

Starting group revision: `91697f2eb9ca51105f8c976d266081b9daa1e7be`.
Data and reference files are read from `liuxin1240013249/data/`:
`defects_android.json`, `defects_linux.json`, `defects_harmony.json`,
`PROVENANCE.json`, and `paper/fig2.csv`, `fig3.csv`, `fig4.csv`.
There are 500 selected records per OS. The author's dashboard source hash in
the baseline provenance is
`93e57bce7ad332b254bd60da4417ae0efb6570448c2a0fa249edd4a6a20a17da`.
Each execution records the exact input and Python-source SHA-256 hashes.

Credit belongs to the paper authors for the data, and to the group baseline for
extracting it, transcribing the reference values, and documenting the category
vocabulary/order. `scripts/core.py` restates that vocabulary and reference
schema with attribution. Statistical, audit and output code is implemented in
this module; no teammate analysis module is imported. Shared inputs and taxonomy
mean the work is not an independent re-annotation of the paper's dataset.

## Experiment A: one factor, shared-zero category policy

For each Figure 4(a–c) dimension and each unordered OS pair, form two aligned
category-frequency vectors. The dimensions have 6 OS layers, 8 affected
functions, and 7 trigger scenarios. Compute Spearman rho as the Pearson
correlation of average ranks, retaining ties. Frequency and proportion ranks
are identical because each OS has the same positive denominator.

Compare (1) all categories with (2) removing only categories for which both
counts are zero. Change no other rule. Save both vectors, category counts,
rho, paper-reference gaps and printed-value agreement. Use the paper's
absolute-rho thresholds: <0.4 weak/none, [0.4,0.6) moderate, [0.6,0.8) strong,
and >=0.8 very strong. These descriptive labels are not significance tests.

Only the Android–HarmonyOS trigger comparison changes on this snapshot:
0.6126374746329801 (7 categories) versus 0.3768511731740915 (6 categories).
The filtered value rounds to the paper's 0.38. This identifies a rule that
explains the value; it does not prove that it was the authors' actual rule.
No severity/code-element dimensions are appended. Overall Figure 4(d) is
excluded because its precise construction is not known.

## Experiment B: one factor, endpoint inclusion

Hold the records, fields, labels, denominators and cut points fixed. Compare:

- Half-open: `[0,c1), [c1,c2), ..., [clast,infinity)`.
- Right-closed: `[0,c1], (c1,c2], ..., (clast,infinity)`.

Cut points are 10,30,50,100 for changed lines; 3,5,10 for involved functions
and modified files. Zero is retained. The unbounded last bin avoids asserting
an undocumented finite value for censored counts; the original printed tail
labels are kept in a separate column. The paper filtered repairs above 500
changed lines, so these histograms describe its selected dataset, not all OS
repairs. The first bin being most frequent does not imply a majority.

An exact count on a cut point moves into the previous bin under the alternative
policy. For a string `k+`, use only the conservative lower-bound interpretation
count >= k. When all possible values have the same membership, assignment is
exact. If baseline membership is ambiguous, stop rather than fabricate its
histogram. For ambiguous alternative membership, a cell's minimum counts only
definitely assigned records and its maximum counts every record that could
belong to it. Per-cell bounds are sharp absent additional information, but
their extremes are linked across cells and cannot be selected independently.

HarmonyOS involved-function `10+` records are CVE-2024-22092,
CVE-2024-28226 and CVE-2024-38386. They are in `[10,infinity)` under the baseline,
but may be in `(5,10]` or `(10,infinity)` under the alternative. The alternative
shares are 5.4–6.0% and 1.8–2.4%. These are identification bounds, **not**
confidence intervals. First-bin shares are exactly identified. Across all nine
OS/metric combinations the first bin remains the unique largest even after
accounting for these bounds.

## Dataset audit and failure policy

Check source hashes, record counts, within-OS Bug ID uniqueness, required
single-label vocabularies, code-element tags, nonnegative count syntax,
addition/deletion arithmetic, zero counts, selected-size cap, shared complete
Patch fields and censored membership. Invalid inputs and ambiguous baseline
assignments block the analysis. Warnings/information are preserved with IDs;
they never silently alter source records.

The arithmetic warning is Linux 2044216: 331 deletions + 28 additions = 359,
while recorded Line Changes = 349. This could reflect a measurement-definition
issue and requires source-level adjudication. Both values are in the same
tail bin; matching aggregate percentages would miss it. No automatic correction
or claim of full-patch validation is made. The other three warnings record the
alternative-policy ambiguities. Informational flags cover 177 zero function
counts, 7 lower-bound counts and 30 groups sharing full Patch fields. A shared
field does not establish duplicate defects or a single true patch entity.

## Repeated runs, comparison and validation

Run at least three actual Python child processes with isolated scratch outputs.
Each yields 135 scalar metrics/bounds: 18 rhos, 39 baseline percentages, and
78 alternative lower/upper percentages. Save actual per-run numbers, execution
logs, UTC start time, elapsed duration, return status, source/input hashes,
checkout revision/dirty state, Python, OS/kernel, CPU and physical memory.
Unavailable environment metadata is explicitly null or marked unavailable.

For each metric calculate the arithmetic mean and sample SD (denominator n−1).
All repeat-run SDs on the current deterministic pipeline are zero. This measures
repeat execution only. It says nothing about label uncertainty, dataset
selection, sampling variance or confidence in generalizing to other defects.

`paper_vs_ours.csv` has 57 rows: 18 candidate-policy rho comparisons and 39
half-open histogram comparisons. Each has the paper value, actual run values,
mean, sample SD, signed gap, absolute gap and relative gap
`abs(mean-paper)/abs(paper)` (NA if paper=0). Percentages and their gaps are
percentage points; rho uses coefficient units. Relative gaps near zero rho are
unstable. Printed agreement means rounding to two decimal places, not exact
unrounded equality or methodological validation. Alternative endpoint bounds
refer to different intervals and are reported as sensitivity contrasts.

Validation recomputes every scientific file, not just match totals. It checks
complete unique metric keys, every per-run value, manifests, all means/SDs,
and regenerated charts, reports and Paper-vs-Ours tables. Hand-checkable unit
tests cover ties, signed correlation, all endpoints, invalid counts, censoring
and conservation. Adversarial tests alter a cell, a run value, a mean, a chart,
or a comparison table to check that stale/tampered artifacts are rejected.
This is consistency validation, not a tamper-proof provenance system or proof
against a coordinated fabricated execution history.

Reruns invalidate the old `verification.json` before testing/writing; standalone
audit, chart generation and verification invalidate it too. Only successful
full verification writes a new success receipt. Analysis reruns discard only
owned `runN_metrics.csv` / `runN.json` / `runN.log` files, so reducing the run
count cannot leave a fourth run behind; unrelated notes are preserved. The
verifier rejects extra run artifacts, checks execution-log hashes and validates
UTC start timestamps and nonnegative finite durations. Report/figure sensitivity
summaries are computed from output rows rather than fixed example values.
Member-scoped `.gitattributes` pins LF for logs, SVGs and HTML too: the group's
existing rules already cover Python/CSV/JSON/Markdown. This prevents Windows
Git line-ending conversion from invalidating otherwise identical artifact and
log hashes after checkout.

## Primary references

1. Zuo, Li and Jiang, *Toward Understanding Operating System Defects*,
   arXiv:2608.20643v1, https://arxiv.org/html/2608.20643v1 . See III-A,
   III-C, IV-A5, IV-C and VI.
2. Author-released dashboard, https://zuohongyao.github.io/ . The analysis uses
   the group's pinned copy, not a live network response at execution time.
3. Group baseline at the starting revision above. Data rights belong to the
   original rights holders; the module's MIT license covers its code.
