# Patch Size vs. Modification Locality: Extending the Comparison to 501–1000 Line Fixes

**Author:** 刘鑫 (1240013249)  
**Track:** CS340 OS-Defects Replication (`Toward Understanding Operating System Defects`, arXiv:2608.20643v1)

## 1. Research Questions

1. Within the paper's `<= 500` changed-line dataset (`n = 1,500`), do smaller patches genuinely concentrate in fewer files and logical modules?
2. After including real `501–1000` changed-line defect-fix patches (excluded by the paper's 500-line refactoring heuristic), do the paper's claims about **localized repairs** and **modular isolation** still hold?

## 2. Unified Definitions & Methodology

### 2.1 Non-Overlapping Size Buckets & Dual Accounting
- **Non-overlapping integer buckets:** `1-9` (`[1,10)`), `10-29` (`[10,30)`), `30-49` (`[30,50)`), `50-99` (`[50,100)`), `100-500` (`[100,500]`), and `501-1000` (`[501,1000]`).
- **Dual line/file accounting:**
  - `raw` scope: all additions + deletions and all modified files in the patch (matching the paper's counting convention, verified on 52 sampled baseline diffs).
  - `prod` scope: excludes `test`, `doc`, and `packaging_or_generated` files so test additions or documentation updates do not inflate production modification scope.

### 2.2 Explicit Module Mapping (`map_path_to_module`)
File counts are **never** equated with module counts. Each file path is deterministically mapped to a logical subsystem/module (full per-file audit in [`results/module_mapping.csv`](results/module_mapping.csv)):
- **Android:** `com/android/server/<subpkg>/...` -> `server/<subpkg>`, `packages/modules/<Mod>/...` -> `modules/<Mod>`, `packages/apps/<App>/...` -> `apps/<App>`, `frameworks/base/<subsys>/...` -> `frameworks/<subsys>`.
- **Linux (`systemd` & kernel):** `src/<component>/...` -> `systemd/<component>` (e.g., `systemd/core`, `systemd/shared`, `systemd/udev`); kernel paths -> `kernel/<subsys>/<name>`.
- **HarmonyOS:** `kernel_liteos_a` -> `<repo>/<layer>/<subsys>`; `rosen/modules/<mod>/...` -> `<repo>/<mod>`; `frameworks/<layer>/<subsys>/...` -> `<repo>/<layer>/<subsys>`.

## 3. Data Sources & Screening Audit

| Dataset / Cohort | Scope | Records | Notes |
| --- | --- | ---: | --- |
| Paper baseline JSON (`../../data/defects_*.json`) | `1–500` lines | 1,500 | 500 per OS; 1 arithmetic mismatch (`LP #2044216`: `28+331=359 != 349`). |
| Baseline diff sample (`data/baseline_diff_sample.json`) | `1–500` lines | 52 | 18 Android, 18 Linux, 16 HarmonyOS real diffs fetched and parsed. |
| Large patch candidates (`data/large_patch_candidates.json`) | `501–1000` lines | 25 | 8 Linux (`systemd`), 14 HarmonyOS (Gitee), 3 Android (AOSP). |
| Audited large defect fixes (`data/large_patch_decisions.csv`) | `501–1000` lines | **7 included / 18 excluded** | 72.0% excluded (test/fuzz-only, feature additions, bulk cleanups, build/merge commits). |
| Teammate `systemd` cohort (`wuyanyang1240009531/...`) | `<=500` lines | 9 mapped (of 11) | Wu Yanyang's Launchpad (`n=3`) and GitHub (`n=6`) `systemd` fixes with file lists. |

All 25 large-patch screening decisions and rationales are recorded in [`data/large_patch_decisions.csv`](data/large_patch_decisions.csv) and [`results/candidate_audit.csv`](results/candidate_audit.csv).

## 4. Key Findings

### 4.1 Full Baseline (`n = 1,500`): Size vs. File Scope
- Across all 1,500 baseline defects, `Line Changes` correlates moderately-to-strongly with `Modified Files`: Android Spearman $\rho = 0.6428$, Linux $\rho = 0.5434$, HarmonyOS $\rho = 0.6334$.
- Moving from `1-9` to `100-500` lines, the multi-file patch rate rises from `19.29%` to `76.92%` (Android), `31.80%` to `84.85%` (Linux), and `12.69%` to `82.35%` (HarmonyOS).

### 4.2 Module-Mapped Cohort (`n = 68`): `<=500` vs. `501–1000`
- **Below 500 lines, multi-file fixes usually stay within one logical module:** Across every bucket from `1-9` through `100-500`, the **median number of production modules touched remains 1.0**, and the cross-module rate stays at **0.0%–18.75%** (even in `100-500`, median files = `4.0` but median modules = `1.0`).
- **Above 500 lines (`501-1000`, `n = 7`), cross-module spread jumps sharply:** Median raw files increases to `17.0`, median production modules rises to `3.0`, and the cross-module rate jumps from `18.75%` to **`71.43%`** (5/7 patches). Yet the mean primary-module line share remains high (`0.8626`), meaning most edits still cluster around one core module with smaller ripple edits in adjacent modules.
- **Same-project `systemd` check with Wu Yanyang's data:** Within Linux `systemd` alone, `Wu_systemd_GH_le500` (`n=6`) has median `1.0` module and `16.67%` cross-module rate, whereas `Ours_systemd_GH_501_1000` (`n=4`) has median `4.0` modules and `75.0%` cross-module rate.

### 4.3 Case Studies
1. **Small but cross-module (`A-374257207`, Android):** Only **6 lines** across 3 files, yet touches **3 distinct modules** (`frameworks/core`, `services/core`, `modules/Permission`), showing that tiny interface/permission fixes can still cross module boundaries.
2. **Large raw size but single-module production fix (`Gitee-security_huks-1497`, HarmonyOS):** **638 raw lines**, but **619 lines (97.0%) are in one unit-test file** (`hks_attest_key_nonids_test.cpp`) while production code changes only **19 lines in 1 file** (`hks_verifier.c`, module `security_huks/frameworks/huks_standard`). Similarly, `GH-systemd-37271` has 551 raw lines but only 325 production lines after excluding tests (`102L`) and man-page docs (`124L`).
3. **Large and genuinely cross-module (`GH-systemd-40007`, Linux):** **850 raw lines** (640 production lines across 6 files and **4 modules**: `systemd/shared`, `systemd/core`, `systemd/analyze`, `systemd/basic`), with `systemd/shared` (`dissect-image.c`, 405 lines) as the primary locus.

## 5. Assessment of the Paper's Explanations & Limitations

- **Evaluation of the >500-line cutoff:** The paper's claim that `>500`-line patches are largely refactoring/non-localized is **partially supported** (`72.0%` of our 501–1000 line candidates were indeed tests, features, or cleanups), **but the cutoff also drops genuine fixes** (`28.0%`) and conflates test/doc lines with production complexity.
- **Evaluation of modularization:** Within `<=500` lines, the paper's modularization conclusion is **strengthened** once file count is separated from module count (median 1.0 module even at 100–500 lines). Above 500 lines, cross-module propagation becomes the norm (`71.43%`).
- **Limitations:** (1) Only 7 included 501–1000 line fixes (and 0 included AOSP fixes among the latest commits inspected, consistent with AOSP's smaller fix granularity); (2) Single-reviewer classification (`single_review`) on the 7 newly included records; (3) Teammate Xiong Yaopeng's time-updated dataset was not yet merged into `origin/main` at submission time, so this study integrates Wu Yanyang's merged `systemd` dataset (`wuyanyang1240009531/`).

## 6. Provenance: Reused vs. New Artifacts

- **Reused unchanged:** `liuxin1240013249/data/defects_*.json`, `scripts/*`, `results/*`, and teammate data in `wuyanyang1240009531/extension/source_sensitivity/`.
- **New in this round:** `extension/patch_locality/{collect.py,analysis.py,test_patch_locality.py,README.md,PRESENTATION.md}`, frozen snapshots in `extension/patch_locality/data/`, and deterministic outputs in `extension/patch_locality/results/`.

## 7. Running Offline

```bash
python extension/patch_locality/analysis.py
python -m unittest extension/patch_locality/test_patch_locality.py -v
```
