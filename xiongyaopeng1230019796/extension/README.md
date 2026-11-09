# Extension experiments

Three follow-up experiments use the same dataset and label mappings as the
reproduction. Run them from the repository folder:

```bash
python extension/subsample_sensitivity.py     # about 40 s
python extension/severity_missing_labels.py   # under a second
python extension/figure4_bootstrap.py          # about 5 s for 10,000 draws
```

Results are committed under `extension/results/`.

The Makefile target extension runs all three experiments. The target
figure4-bootstrap runs only the Figure 4 uncertainty experiment.

## 1. Sample-size sensitivity

The paper computes every distribution from 500 defects per operating system, and
its main statements are about which category is the largest. The question here is
whether that ranking survives when fewer defects are sampled.

For n in {50, 100, 200, 300, 400, 500} the script draws 500 subsamples per
(OS, dimension, run) without replacement. It records how often the full-sample
top category is still the top category, and the share of that category. Three
runs with different seeds give the mean and standard deviation over run-level
means. A separate bootstrap (1,000 resamples with replacement) puts a 95%
interval on each of the 114 Table II percentages.

At n = 100, 11 of the 15 (OS, dimension) pairs still recover the full-sample top
category in at least 99% of subsamples. Three do not:

| OS | Dimension | Recovery at n=100 |
| --- | --- | ---: |
| HarmonyOS | affected function | 63.73% ± 0.76 |
| Linux | code elements | 76.53% ± 0.50 |
| Android | trigger scenario | 76.80% ± 0.72 |

All three have a close runner-up, so the rank can flip in a sizeable minority of
100-defect samples. The headline categories (Android System Service Layer
38.80%, Linux Application Layer 54.20%, HarmonyOS Kernel Layer 71.80%) are
recovered in at least 99.67% of subsamples at n = 100.

The bootstrap file shows the same per cell: dominant categories are tightly
bounded, rare ones are not (Android Runtime/Virtual Machine Layer 0.40%, 95%
interval [0.00, 1.00]).

Files: `results/subsample_sensitivity.csv`, `results/subsample_sensitivity.md`,
`results/table2_bootstrap_ci.csv`.

## 2. Missing severity labels

65.20% of the Linux defects have no severity label (`Undecided`), against 1.20%
for HarmonyOS and none for Android. The paper counts `Undecided` as a category;
this experiment removes it from the denominator and recomputes the shares.

For Linux the top category changes from `Undecided` (65.20%) to `High`, whose
share among the labelled records is 53.45%, against 18.60% under the paper's
treatment. For HarmonyOS the six missing records shift the shares by at most
0.62 pp and do not change the ranking; Android is unaffected.

Files: `results/severity_missing_labels.csv`,
`results/severity_missing_labels.md`.

## 3. Uncertainty in Figure 4 correlations

The existing reproduction matches the nine Figure 4(a-c) Spearman coefficients
to the paper. This experiment asks whether those point estimates are stable
when the 500 defect records per OS are resampled. It excludes panel (d), whose
construction is unspecified and whose printed values do not match the released
records in the existing replication.

For each of 10,000 replicates, the script samples 500 records with replacement
within each OS, rebuilds all three distributions from the same sampled records,
and recomputes the nine OS-pair correlations. It reports percentile 95%
intervals, the fraction of replicates with the same sign as the observed
coefficient, and the fraction below the paper's absolute-rho 0.4 weak-correlation
boundary. The shared-zero category rule and category order are inherited from
`scripts/common.py`.

All nine original coefficients match the paper at two-decimal precision. Four
of the nine bootstrap intervals exclude zero: Android-HarmonyOS OS layer
([-0.89, -0.26]), Android-HarmonyOS affected function ([0.10, 0.69]),
Linux-HarmonyOS affected function ([-0.60, -0.19]), and Android-HarmonyOS
trigger scenario ([0.09, 0.60]). The other five intervals include zero. This
supports some cross-OS differences but does not establish that every pair and
dimension differs robustly.

These are resampling sensitivity intervals conditional on the released records,
not population-level confidence intervals. The paper selected the latest 500
records per OS rather than a probability sample, and each correlation is across
only 6-8 fixed categories. The result should not be generalized to all OS defects.

Files: `results/figure4_bootstrap.csv` and `results/figure4_bootstrap.md`.
Defaults: 10,000 resamples, seed `20261109`; both can be changed with
`--bootstrap-resamples` and `--seed`. The report records input file hashes and
the Python version used.

## Re-running

`make extension` runs all three scripts. They write to `extension/results/` by
default; `--out-dir` changes that.
