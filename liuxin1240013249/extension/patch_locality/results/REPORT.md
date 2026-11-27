# Patch Size vs. Modification Locality Report

## 1. Full Baseline (n = 1,500)

- Spearman correlation (`Line Changes` vs `Modified Files`): Android `0.6428`, Linux `0.5434`, HarmonyOS `0.6334`.
- Arithmetic audit (`Line Additions + Line Deletions == Line Changes`): 1,499/1,500 exact; 1 discrepancy in Linux `LP #2044216` (`28 + 331 = 359` vs reported `349`).
- Baseline diff sample verification: 19/52 sampled patches match the paper's `Line Changes` and `Modified Files` counts exactly (confirming the paper counts raw diff lines/files including tests/docs/packaging).

## 2. 501–1000 Line Candidate Screening

- Audited 25 candidates in the 501–1000 raw-line window: **7 included** as genuine defect fixes, **18 excluded** (72.0%: test-only/fuzzing, feature additions, bulk warning/dead-code cleanup, build migrations, or branch merges).
- Notably, 2 of the 7 included 501–1000 line fixes drop below 500 lines when counting production code only (`Gitee-security_huks-1497`: raw 638L / prod 19L across 1 file; `GH-systemd-37271`: raw 551L / prod 325L).

## 3. Module-Mapped Cohort Comparison

| Bucket | n | Median Raw Lines | Median Prod Lines | Median Files | Median Prod Modules | Cross-Module % | Mean Primary Share |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1-9 | 12 | 5.5 | 4.0 | 1.0 | 1.0 | 16.67% | 0.625 |
| 10-29 | 12 | 18.0 | 15.0 | 1.0 | 1.0 | 0.0% | 0.9167 |
| 30-49 | 10 | 34.5 | 32.5 | 1.0 | 1.0 | 0.0% | 0.7 |
| 50-99 | 11 | 78 | 53 | 3 | 1 | 18.18% | 0.627 |
| 100-500 | 16 | 221.5 | 105.0 | 4.0 | 1.0 | 18.75% | 0.7689 |
| 501-1000 | 7 | 638 | 549 | 17 | 3 | 71.43% | 0.8626 |

## 4. Same-Project Check on Linux `systemd` (with Wu Yanyang's Data)

| Cohort | n | Median Raw Lines | Median Prod Lines | Median Files | Median Prod Modules | Cross-Module % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Wu_systemd_LP_le500 | 3 | 21 | 21 | 2 | 1 | 33.33% |
| Wu_systemd_GH_le500 | 6 | 115.0 | 63.5 | 3.5 | 1.0 | 16.67% |
| Ours_systemd_GH_501_1000 | 4 | 759.5 | 571.5 | 18.0 | 4.0 | 75.0% |
