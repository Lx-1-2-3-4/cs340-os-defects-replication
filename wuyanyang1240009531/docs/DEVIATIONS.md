# Explicit settings and deviations

This table distinguishes author statements from inferred reconstruction choices
and this module's extension. An unspecified setting must not be filled in as a
known fact about the author's implementation.

| Item | Original paper/release | Setting used here | Reason and consequence |
| --- | --- | --- | --- |
| Scale | Released labelled samples, 500 per OS | Same 1,500 records pinned by baseline provenance | Fixed-input aggregation replication, not new defect collection |
| Annotation | Author-provided taxonomy and labels | Reuse existing labels, no re-annotation | Isolates preprocessing; cannot validate label accuracy |
| Author executable/environment | Full original calculation code and environment are not supplied with the inputs used here | Standard-library Python implementation; actual environment in per-run JSON | Reconstruct published statistics; not an exact recreation of author software |
| Shared-zero categories | Treatment not sufficiently specified to establish the precise rule | Full taxonomy versus dropping pairwise shared zeros | Single-factor contrast; filtered agreement is not proof of author intent |
| Rank ties | Spearman rho named; full implementation unavailable | Average ranks, Pearson correlation of ranks | Explicit and hand-testable convention |
| Histogram endpoints | Finite printed range labels; prose and matching numerical convention differ at endpoints | Half-open reconstruction versus right-closed contrast | Both definitions shown; no claim that their percentages estimate the same interval |
| Tail bins | Finite labels such as 100–500 and 10–50 | Last bins explicitly unbounded; original label retained separately | Avoids an invented finite value for a lower-bound observation; input selection cap is still disclosed |
| Lower-bound strings | Released counts include `10+`, `20+` | Interpret only as >= bound; alternative memberships may be set-valued | No numeric-prefix imputation; identification bounds propagated |
| Zero involved functions | 177 zero values in released records | Retain and flag as context | Zero is not automatically missing or an error |
| Line-count arithmetic | Linux 2044216 total349 versus 331+28=359 | Flag; keep349 unchanged | No unverified source-data repair; aggregate histogram cannot distinguish these values |
| Shared complete Patch fields | Multiple defects can share a field value | Report groups; no automatic deduplication | Shared strings do not prove duplicate observations |
| Figure4d Overall | Construction unresolved; group has documented mismatch | Exclude from this module | Avoid silently replacing the author's metric with a candidate construction |
| Repeated runs | Course requires >=3 actual runs | Three subprocesses, actual mean/sample SD and hash comparisons | Deterministic SD=0 measures execution repeatability only |
| Environment pinning | Author system image/kernel not established | Optional Python3.12.7 Debian Bookworm recipe; CI Ubuntu22.04/Python3.12.7; local Windows/Python version recorded | Local run differs from configured container/CI. Neither remote environment is claimed tested; host kernel is recorded rather than pinned by Docker |

The two policy experiments are separate. Dataset, hardware, workload, metric,
taxonomy and all other preprocessing remain fixed within each contrast. Both
are deterministic descriptive experiments; no random-seed parameter is needed.

Changed group files are only `README.md` (member row) and
`.github/workflows/ci.yml` (additional isolated job). All member code, tests,
documentation, configuration and generated evidence are new files under
`wuyanyang1240009531/`; existing teammate files are not modified.
