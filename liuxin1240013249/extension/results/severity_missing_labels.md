# Extension 2: missing severity labels

The paper's severity comparison includes a large 'Undecided' category
(Linux 65.20%). This experiment
removes it from the denominator and recomputes the shares, leaving the
records and labels unchanged.

## Top category under both treatments

| OS | Missing labels | Top category (paper treatment) | Top category (labeled only) |
| --- | ---: | --- | --- |
| Android | 0/500 (0.00%) | High | High |
| Linux | 326/500 (65.20%) | Undecided | High |
| HarmonyOS | 6/500 (1.20%) | Medium | Medium |

Per-category shares under both treatments:

| OS | Category | With missing (%) | Labeled only (%) | Change (pp) |
| --- | --- | ---: | ---: | ---: |
| Android | Critical | 8.60 | 8.60 | +0.00 |
| Android | High | 91.00 | 91.00 | +0.00 |
| Android | Medium | 0.40 | 0.40 | +0.00 |
| Android | Low | 0.00 | 0.00 | +0.00 |
| Android | Undecided | 0.00 | n/a | n/a |
| Linux | Critical | 2.60 | 7.47 | +4.87 |
| Linux | High | 18.60 | 53.45 | +34.85 |
| Linux | Medium | 11.40 | 32.76 | +21.36 |
| Linux | Low | 2.20 | 6.32 | +4.12 |
| Linux | Undecided | 65.20 | n/a | n/a |
| HarmonyOS | Critical | 0.20 | 0.20 | +0.00 |
| HarmonyOS | High | 22.40 | 22.67 | +0.27 |
| HarmonyOS | Medium | 51.40 | 52.02 | +0.62 |
| HarmonyOS | Low | 24.80 | 25.10 | +0.30 |
| HarmonyOS | Undecided | 1.20 | n/a | n/a |

## What this says

Android has no missing labels, so nothing changes (High stays
the most frequent severity). On Linux, dropping the missing records raises
High from 18.60% to 53.45%
and makes it the most frequent labelled severity; with the paper's treatment
the top category is Undecided instead. HarmonyOS has only
6 missing records, too few to change the ranking (Medium remains first).

So the cross-OS severity comparison in Table II is partly a comparison of
label availability rather than of severity itself, and the Linux numbers
should be read conditional on that.

Numbers written by `extension/severity_missing_labels.py`.
