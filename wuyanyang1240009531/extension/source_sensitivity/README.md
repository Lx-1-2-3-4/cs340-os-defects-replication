# Source sensitivity of Linux systemd defects

吴彦阳 · 1240009531 · CS340

## Question and result

How sensitive are defect distributions to the choice between Ubuntu Launchpad and upstream GitHub when the project, date window and taxonomy are held as comparable as the available evidence allows?

The primary cohorts contain **5 Launchpad and 6 GitHub defects**. Three Launchpad records have confirmed environment-dependent triggers. The GitHub cohort has zero confirmed environment-dependent triggers and one unresolved trigger. The all-layer Launchpad share is 60.0% and the GitHub share is bounded by 0–16.7% within these records. The bounds assign each unknown trigger to environment or to another category and retain all records in the denominator.

| Environment trigger comparison | Launchpad | Upstream GitHub | GitHub minus Launchpad (pp) |
|---|---:|---:|---:|
| All layers | 3/5 | 0–1/6 | −60.0 to −43.3 |
| System service, harmonized labels | 2/4 | 0–1/3 | −50.0 to −16.7 |
| System service, original Launchpad labels | 0/1 | 0–1/3 | 0.0 to +33.3 |
| Directly comparable diffs, all layers | 2/3 | 0–1/6 | −66.7 to −50.0 |
| Include borderline test-origin PR #30138, all layers | 3/5 | 0–1/7 | −60.0 to −45.7 |

The all-layer direction survives these checks in this specific sample. The same-layer direction depends on the layer mapping. With the author labels there is only one downstream service-layer record, so the within-layer evidence is inconclusive. These bounds account for the unknown label and describe the observed records. Sampling and selection uncertainty remain. Trigger Spearman is withheld because one GitHub trigger is unresolved. Category counts and denominators are the primary evidence.

## Sources and scope

| Source | Candidate frame | Coverage and selection |
|---|---|---|
| Paper-released Linux cohort | 500 records from the group snapshot | Published labels and fixes provide the reference frame. No per-record dates in the released JSON. |
| Ubuntu Launchpad systemd | 8 author-snapshot rows identified by an explicit systemd GitHub or Ubuntu source-package patch URL | Ubuntu package issues, integration and backports. Confirmed each package task and joined the report creation date and release date via the Launchpad API. URL identification can miss aliases or other patch hosts. |
| GitHub systemd/systemd | 48 PRs retained from search results, 12 per merge-date block | Upstream reports and fixes. Each block keeps the first 12 PRs by PR creation time in a search for merged PRs with a Fixes reference. This purposive frame favors explicitly linked issues and early PRs within each block. It allows repeatable screening of the frozen results and has limited coverage. |

Candidate periods are May–December 2023 and the three subsequent half-year blocks through June 2025. Both report creation and fix event must fall within 2023-05-01 through 2025-06-30 UTC. The fix event means PR merge upstream and package fix released downstream. Report date and fix event are separate fields. The author snapshot and GitHub search have different selection mechanisms. Upstream versus downstream report populations, versions, and evidence availability remain confounded with source. The study covers Linux systemd only.

Sources include [paper §III and §IV](https://arxiv.org/html/2608.20643v1#S3), [author data](https://zuohongyao.github.io/), [Ubuntu systemd bugs](https://bugs.launchpad.net/ubuntu/+source/systemd), and [systemd upstream](https://github.com/systemd/systemd).

## Screening, deduplication, and classification

1. Keep an ordinary issue linked to a verifiable fix. For the GitHub frame, require exactly one parsed closing issue reference, a closed issue and a merged fix. Exclude enhancements, test-only concerns, and fixes whose scope cannot be attributed to the report. The #30138 report establishes an intermittent integration-test failure. Its production changes warrant a sensitivity case, while the primary cohort requires clearer product-defect evidence. PR #35694 also has uncertain product impact and remains excluded.
2. Apply the paper's ceiling of 500 changed lines. Count additions plus deletions. The initial ceiling uses GitHub PR totals and the paper's recorded Linux totals. Three included downstream fixes have a direct diff whose addition and deletion counts match the reference. Two are packaging diffs (#2102236 and #2077779) with identifiable report-specific payloads. The main comparison retains their published counts, and the direct-diff analysis excludes both. LP #2100252 has multiple nested backports, and #2109890 links to documentation. Both are excluded. The primary upstream subset contains six matching direct diffs.
3. Use the source-qualified defect ID as the row key. Check repeated GitHub issue IDs and merge SHAs, compare upstream commit references against commit URLs across all 500 published rows, and check explicit issue/backport references in the inspected diffs and eight Launchpad report descriptions. For example, LP #2052137 links to upstream issue #31165 and PR #31172. Neither is in this GitHub candidate frame. These checks found no positive match between the included cohorts. Unlinked and rewritten backports can escape detection. Each cohort has its own denominator.
4. Apply the paper's OS layer, affected function and trigger vocabulary to both groups. Use the available public reports and inspected patch evidence together. Keep the author's tags alongside the harmonized downstream tags. Three Launchpad layers change, including LP #2077779, whose repair payload targets udev. LP #2052137 is coded State Dependency because the report specifies reconfiguration and gives insufficient evidence to establish concurrency. GitHub issue #35798 is marked Unknown for its trigger because the distinction between external environment and an exceptional system state is unresolved. Severity retains source labels where available and stays outside the comparisons. Code-element tags and function counts are outside this extension's measured outcomes.
5. The decisions and explanations are in decisions.csv. Codex conducted the evidence review and prepared the provisional labels. A teammate has yet to independently adjudicate the ambiguous cases. Each included row records single-review status. The experiment compares public records and patch metadata.

## Replay and files

Use Python 3.12 from this directory. The analysis uses the standard library and imports the existing member module's paper vocabulary and Spearman implementation. The committed group dataset is resolved from the extension path, and its hash is verified.

    python -B analysis.py
    python -B verify.py

The verifier checks the saved cohort and replays the analysis in three separate processes in temporary directories. Each generated file must match the saved output byte for byte. It refreshes results/local_verification.json on success. The receipt records computational repeatability for the frozen inputs. The six decisions in the peer review queue still need independent adjudication.

## Independent review handoff

Start with the six rows in [the review queue](results/peer_review_queue.csv). Use the linked report and fix to record a proposed decision, category and evidence in a separate copy of the queue. The five high-impact questions are the three changed downstream layers, the reconfiguration-versus-concurrency trigger choice, and the unresolved GitHub trigger. Also assess the borderline integration-test record. For the two packaging records, note whether the reported fix can be separated from packaging metadata. Apply agreed changes in decisions.csv and rerun both commands above. Keep unresolved judgments visible and retain the published labels in the comparison.

Expected output is a short cohort summary and CSV, JSON, and SVG files under results. Replay runs offline and typically takes under a few seconds.

- study_snapshot.json contains frozen search queries, metadata, retrieval timestamp and baseline hash.
- patch_evidence.json records inspected diff URLs, status, SHA-256, line counts and file metadata. report_links.json records GitHub references extracted from the eight Launchpad report descriptions.
- decisions.csv holds review decisions and reasons. The program composes these with automated checks in results/candidate_audit.csv.
- results/defects.csv is the compact peer handoff with source identifiers, issue and fix links, dates and date types, patch counts, taxonomy, evidence and original labels.
- results/peer_review_queue.csv lists high-priority pending decisions for independent teammate review.
- results/distribution.csv covers all categories including zeros, same-layer comparisons, direct diffs and an original-label sensitivity analysis. An unavailable percentage has a blank cell.
- results/spearman.csv records coefficients and withholding reasons. Within a fixed layer, layer correlation is omitted. The three-record minimum is a reporting rule for sparse groups.
- results/environment_sensitivity.csv contains confirmed counts, unknown counts and feasible percentage-point gap bounds for each comparison.
- results/layers.svg and results/service_triggers.svg display count and denominator information.
- results/summary.json records replay inputs and code hashes.

For an optional future metadata refresh, run collect.py and patch_metadata.py with public API access. To recheck report references against the existing cohort, run `python -B collect.py --report-links study_snapshot.json`. Capture collection output separately and review it against the dated study. Search results may evolve. The default replay uses the frozen metadata. The earlier member contribution, group reference dataset and paper reproduction supplied the underlying vocabulary, ranking method and fixed downstream frame. This extension adds the upstream frame, project/date matching, evidence review, alternate label and patch-count checks, and source comparisons.

Prepared with Codex assistance for public metadata retrieval, analysis code, provisional review decisions, testing and drafting.
