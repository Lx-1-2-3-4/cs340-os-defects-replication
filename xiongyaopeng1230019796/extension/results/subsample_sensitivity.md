# Extension 1: sample-size sensitivity

The paper uses 500 defects per system. This experiment asks how much of the
ranking survives at smaller sample sizes. For every n in [50, 100, 200, 300, 400, 500] it draws
500 subsamples per (OS, dimension, run) without replacement, in
3 runs with seeds 20261105..20261107; the numbers
below are the mean and standard deviation across the three run-level means.
The dataset, label mappings and statistic are the same as in the reproduction.

## Recovery rate of the full-sample top category (%)

| OS | Dimension | n=50 | n=100 | n=200 | n=300 | n=400 | n=500 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Android | os_layer | 94.40 +/- 0.53 | 99.67 +/- 0.12 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 |
| Android | affected_function | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 |
| Android | trigger_scenario | 66.00 +/- 2.27 | 76.80 +/- 0.72 | 89.20 +/- 0.53 | 97.00 +/- 0.87 | 99.93 +/- 0.12 | 100.00 +/- 0.00 |
| Android | severity | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 |
| Android | code_element | 83.93 +/- 0.42 | 92.80 +/- 0.69 | 99.47 +/- 0.58 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 |
| Linux | os_layer | 99.87 +/- 0.12 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 |
| Linux | affected_function | 98.93 +/- 0.12 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 |
| Linux | trigger_scenario | 99.93 +/- 0.12 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 |
| Linux | severity | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 |
| Linux | code_element | 61.93 +/- 1.33 | 76.53 +/- 0.50 | 92.00 +/- 2.80 | 98.27 +/- 0.23 | 100.00 +/- 0.00 | 100.00 +/- 0.00 |
| HarmonyOS | os_layer | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 |
| HarmonyOS | affected_function | 51.73 +/- 0.81 | 63.73 +/- 0.76 | 77.00 +/- 1.25 | 87.60 +/- 1.40 | 97.13 +/- 0.31 | 100.00 +/- 0.00 |
| HarmonyOS | trigger_scenario | 99.73 +/- 0.23 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 |
| HarmonyOS | severity | 99.20 +/- 0.35 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 |
| HarmonyOS | code_element | 94.53 +/- 1.01 | 99.13 +/- 0.58 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 | 100.00 +/- 0.00 |

## Share of the full-sample top category (%, mean +/- sd across runs)

| OS | Dimension | n=50 | n=100 | n=200 | n=300 | n=400 | n=500 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Android | os_layer | 38.86 +/- 0.55 | 38.79 +/- 0.27 | 38.83 +/- 0.17 | 38.78 +/- 0.01 | 38.78 +/- 0.08 | 38.80 +/- 0.00 |
| Android | affected_function | 60.01 +/- 0.26 | 59.84 +/- 0.10 | 60.04 +/- 0.14 | 60.02 +/- 0.10 | 60.02 +/- 0.01 | 60.00 +/- 0.00 |
| Android | trigger_scenario | 36.89 +/- 0.05 | 36.91 +/- 0.08 | 36.96 +/- 0.11 | 37.02 +/- 0.11 | 37.00 +/- 0.01 | 37.00 +/- 0.00 |
| Android | severity | 90.97 +/- 0.33 | 91.08 +/- 0.02 | 91.05 +/- 0.06 | 90.99 +/- 0.02 | 91.02 +/- 0.04 | 91.00 +/- 0.00 |
| Android | code_element | 63.34 +/- 0.11 | 63.40 +/- 0.17 | 63.44 +/- 0.04 | 63.33 +/- 0.04 | 63.43 +/- 0.01 | 63.40 +/- 0.00 |
| Linux | os_layer | 54.05 +/- 0.18 | 54.44 +/- 0.10 | 54.23 +/- 0.07 | 54.23 +/- 0.05 | 54.23 +/- 0.04 | 54.20 +/- 0.00 |
| Linux | affected_function | 41.42 +/- 0.34 | 41.21 +/- 0.22 | 41.33 +/- 0.12 | 41.13 +/- 0.03 | 41.21 +/- 0.01 | 41.20 +/- 0.00 |
| Linux | trigger_scenario | 61.93 +/- 0.16 | 62.06 +/- 0.09 | 62.11 +/- 0.06 | 62.03 +/- 0.09 | 61.98 +/- 0.05 | 62.00 +/- 0.00 |
| Linux | severity | 65.25 +/- 0.12 | 65.31 +/- 0.31 | 65.22 +/- 0.22 | 65.17 +/- 0.06 | 65.17 +/- 0.00 | 65.20 +/- 0.00 |
| Linux | code_element | 54.30 +/- 0.29 | 54.35 +/- 0.14 | 54.46 +/- 0.14 | 54.45 +/- 0.08 | 54.42 +/- 0.03 | 54.40 +/- 0.00 |
| HarmonyOS | os_layer | 71.90 +/- 0.27 | 71.70 +/- 0.17 | 71.79 +/- 0.05 | 71.77 +/- 0.04 | 71.83 +/- 0.03 | 71.80 +/- 0.00 |
| HarmonyOS | affected_function | 22.75 +/- 0.26 | 22.82 +/- 0.12 | 22.80 +/- 0.17 | 22.79 +/- 0.03 | 22.79 +/- 0.01 | 22.80 +/- 0.00 |
| HarmonyOS | trigger_scenario | 52.24 +/- 0.27 | 52.75 +/- 0.12 | 52.65 +/- 0.16 | 52.59 +/- 0.13 | 52.63 +/- 0.05 | 52.60 +/- 0.00 |
| HarmonyOS | severity | 51.47 +/- 0.20 | 51.35 +/- 0.25 | 51.38 +/- 0.06 | 51.44 +/- 0.07 | 51.32 +/- 0.03 | 51.40 +/- 0.00 |
| HarmonyOS | code_element | 61.92 +/- 0.07 | 61.82 +/- 0.23 | 61.88 +/- 0.01 | 61.80 +/- 0.07 | 61.86 +/- 0.10 | 61.80 +/- 0.00 |

## What this says

At n = 100, 11 of the 15 (OS, dimension) pairs still recover the
full-sample top category in at least 99% of subsamples. The three weakest
pairs at n = 100 are:

| OS | Dimension | Top-category recovery at n=100 (%) |
| --- | --- | ---: |
| HarmonyOS | affected_function | 63.73 |
| Linux | code_element | 76.53 |
| Android | trigger_scenario | 76.80 |

Most of the paper's rank statements are therefore stable at a fifth of its
sample, but these three are not: they hold in the majority of 100-defect
subsamples without holding in almost all of them. The bootstrap file makes
the same point per cell: rare categories such as Android Runtime/Virtual
Machine Layer (0.40%) have wide intervals relative to their value, while
the dominant categories are tightly bounded.

Numbers written by `extension/subsample_sensitivity.py`.
