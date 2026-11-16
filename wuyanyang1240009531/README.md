# Preprocessing sensitivity and dataset consistency

Member: **吴彦阳 (1240009531; Wu Yanyang)**.

This contribution tests how two explicit preprocessing choices affect the
group's replication of *Toward Understanding Operating System Defects*
(arXiv:2608.20643v1). It adds an independent implementation of the audit and
contrasts, rather than another copy of the complete baseline. It uses the
existing data in `../liuxin1240013249/data/` without modifying it.

## Run locally

Requirements: Python **3.10+**, standard library only. The group CI and optional
container specify Python **3.12.7**. No package installation, network request,
GPU, OS-kernel build or vulnerability execution is needed. Keep this directory
beside `liuxin1240013249/` in the group repository. Git is optional at execution
time; a source export records null for unavailable checkout metadata.

From the **group repository root**, run:

```sh
python -B wuyanyang1240009531/scripts/run_all.py
```

This runs the tests, starts three actual analysis processes, records their
outputs, computes means and sample standard deviations, generates two SVG charts
and an English report, and verifies all scientific cells and generated reports.
It performs no commit, push or upload. Allow roughly 15–60 seconds on an ordinary
laptop; runtime depends on the filesystem, CPU and test environment. Actual
analysis-process durations and environment are recorded in `results/logs/`.

On systems where the executable is `python3`, substitute `python3`. On Windows,
use an installed Python executable if the `python` command opens the Microsoft
Store. Paths containing spaces are supported. Optional Make targets from this
member directory are `make all`, `make test`, and `make verify`; `PYTHON` can be
overridden.

To regenerate in a separate directory:

```sh
python -B wuyanyang1240009531/scripts/run_all.py --out-dir "review output"
python -B wuyanyang1240009531/scripts/verify_results.py --out-dir "review output"
```

The output must not overlap the input directories. `--runs N` accepts N >= 3.
`--data-dir` and `--paper-dir` support relocation of the same pinned fixture;
the regression tests intentionally use the group's original snapshot. This is
not a general-purpose analyzer for arbitrary schemas or new datasets.

## Read the evidence

Start with [`results/REPORT.html`](results/REPORT.html), a self-contained offline
English report with embedded charts. The Markdown source is
[`results/REPORT.md`](results/REPORT.md).

| Evidence | File |
| --- | --- |
| Paper vs. each run, mean ± sample SD, gaps, candidate setting | `results/paper_vs_ours.csv` (57 rows) |
| Nine all-category / shared-zero-filter contrasts | `results/zero_policy_comparison.csv` |
| Exact category vectors | `results/correlation_vectors.csv` |
| 39 endpoint comparisons, including identification bounds | `results/binning_comparison.csv` |
| Every OS / Bug ID / metric assignment | `results/bucket_membership.csv` (4,500 rows) |
| Moved or ambiguously assigned records | `results/boundary_records.csv` |
| Audit flags and input checks | `results/data_audit.csv`, `audit_checks.csv` |
| Actual per-run values and statistics | `results/runs/`, `run_statistics.csv` |
| Execution logs, source/input hashes, hardware/software | `results/logs/` |
| Full verification and repeatability | `results/verification.json`, `determinism.json` |
| Automatically generated charts | `results/figures/zero_policy.svg`, `binning_policy.svg` |

On the pinned snapshot, all-category correlation agrees with 8/9 printed values;
removing shared-zero categories agrees with 9/9. Android–HarmonyOS trigger-scenario
rho changes from 0.612637 to 0.376851. The half-open histograms agree with 39/39
printed cells; the largest endpoint-induced change is 14.4 percentage points.
Three HarmonyOS `10+` counts require bounds under the alternative policy. The
audit has 0 blocking errors, 4 warnings and 214 informational flags. These
agreements do not establish the authors' unpublished preprocessing method.

## Integration and scope

- [Methods and interpretation](docs/METHODS.md)
- [Deviations and explicit settings](docs/DEVIATIONS.md)
- [Member contribution and attribution](docs/MEMBER_CONTRIBUTION.md)
- [AI usage and review responsibilities](docs/AI_USAGE.md)
- [Group report integration and remaining requirements](docs/GROUP_INTEGRATION.md)
- [Branch, PR and submission workflow](docs/SUBMISSION_WORKFLOW.md)

After changing code or regenerating artifacts, require a fresh successful
`results/verification.json`. Old success receipts are invalidated before reruns;
the verifier also checks execution-log hashes and rejects extra run artifacts.

The baseline, JSD, sample-size/severity/weighting and bootstrap contributions
remain in their original members' directories. Figure 4(d) remains unresolved
and is not counted as reproduced here. No source-patch relabelling or repair is
claimed. This supplement is **not the complete group final PDF**.

## Optional container and CI

From the group repository root:

```sh
docker build -f wuyanyang1240009531/Dockerfile -t cs340-wu-audit:local .
docker run --name cs340-wu-audit-check cs340-wu-audit:local
docker cp cs340-wu-audit-check:/app/wuyanyang1240009531/results ./wu-container-results
```

The container has no third-party Python dependencies. The base-image tag specifies
Python and Debian Bookworm, not an immutable image digest or host kernel. Container
execution still needs to be tested on a machine with a working Docker daemon;
do not treat this recipe as a successful Docker-run record. The separate
`preprocessing-audit` CI job is configured at the repository root. Remote CI
success must be established after an authorized upload; local results do not
prove remote CI success.
