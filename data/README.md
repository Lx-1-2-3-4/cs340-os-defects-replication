# Dataset snapshot — released defect records

This directory contains the snapshot of the dataset released by the authors of
*Toward Understanding Operating System Defects* (arXiv:2608.20643v1) that is used
for the reproduction.

## Contents

| File | Records | Unique bug IDs | Bytes |
| --- | ---: | ---: | ---: |
| `defects_android.json` | 500 | 500 | 252,810 |
| `defects_harmony.json` | 500 | 500 | 238,848 |
| `defects_linux.json` | 500 | 500 | 278,850 |
| `PROVENANCE.json` | — | — | source URL, retrieval time, SHA-256 hashes |

The three JSON files are arrays of objects, one object per defect. All 1,500
records were released by the authors; nothing is sampled or filtered here.

## Provenance

The authors publish the data through a dashboard at <https://zuohongyao.github.io/>.
The dashboard is a single HTML page whose JavaScript embeds the complete dataset
as `var DATA = { android: [...], harmony: [...], linux: [...] }`. The retrieval
script (`scripts/fetch_data.py`) downloads the page, extracts the three arrays
with the standard library, validates them and writes this snapshot together with
`PROVENANCE.json`:

* source URL and exact bytes downloaded,
* SHA-256 of the downloaded page,
* retrieval timestamp (UTC),
* SHA-256, record count and unique bug ID count of every output file.

The snapshot is committed so the reproduction runs offline on exactly these
bytes, even if the authors update the live dashboard. Refreshing it is a separate
step:

```bash
python scripts/fetch_data.py            # refresh snapshot + PROVENANCE.json
python scripts/fetch_data.py --check    # verify committed files against hashes
python scripts/fetch_data.py --check --verify-remote   # also compare with the live page
```

## Record schema

| Field | Type | Meaning (paper dimension) |
| --- | --- | --- |
| `Bug ID` | string | Defect identifier (Android `A-…`, HarmonyOS `CVE-…`, Linux Bugzilla ID) |
| `_idx` | integer | Original row index in the released dashboard |
| `Severity Level` | string | Severity (Table II, severity panel) |
| `OS Layer` | string | OS layer where the defect occurs (Table II) |
| `Affected Function` | string | OS function affected by the defect (Table II) |
| `Trigger Scenario` | string | Condition that triggers the defect (Table II) |
| `Code Level` | string, comma-separated | Repaired code elements, **multi-label** (Table II) |
| `Line Deletions` / `Line Additions` / `Line Changes` | integer | Patch size (Figure 2) |
| `Involved Functions` / `Modified Files` | integer | Patch breadth (Figure 3) |
| `Patch` | URL | Link to the public fix |

The long labels used in the dashboard are translated to the paper's short table
labels by the dictionaries in `scripts/common.py`; an unseen label aborts the
reproduction instead of being silently ignored.

## Known quirks of the released data (all handled by the code)

1. **HarmonyOS `Involved Functions` is stored as strings**, and some values are
   capped (`"20+"`). The code parses the integer prefix; the cap only affects the
   open-ended last bucket of Figure 3, so the reported bucket counts are
   unaffected (`scripts/common.py::numeric`).
2. **Missing severity labels are named differently.** Linux uses `Undecided`
   (326 records, 65.20%), HarmonyOS uses `Unknown` (6 records, 1.20%). Both are
   reported as `Undecided` in Table II, which is what makes the 1.20% HarmonyOS
   value reproduce exactly (`scripts/common.py::SEVERITY_LABEL`).
3. **`Code Level` is multi-label** (`"Entire Function, If, Function Call"`).
   A defect therefore contributes to several code-element percentages; the
   percentages in the paper's last Table II panel sum to more than 100%.
4. **The dashboard contains a fourth top-level array, `datasets`**, which is
   Chart.js configuration and not defect data. The fetch script ignores it.
5. **The live page can change.** Two downloads a few minutes apart can differ in
   a few bytes (the page includes generated content), while the defect arrays are
   unchanged. That is why the snapshot and its hashes are committed.

## Integrity check

```bash
python scripts/fetch_data.py --check
```

prints one line per file and fails if any SHA-256 differs from `PROVENANCE.json`.

## Licence and attribution

The records are the authors' released dataset
(Hongyao Zuo, Jiali Li, Jiajun Jiang, *Toward Understanding Operating System
Defects*, arXiv:2608.20643v1). They are redistributed here **for academic
reproduction only**, with attribution. The MIT licence in the repository root
applies to our code, not to this dataset.
