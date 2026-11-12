# Extension experiments

Three experiments change one factor at a time, using the same dataset and label
mappings as the reproduction. Run the commands from the project folder.

```bash
python extension/subsample_sensitivity.py     # about 40 s
python extension/severity_missing_labels.py   # under a second
python extension/patch_link_weighting.py
```

Results are committed under `extension/results/`.

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

## 3. Patch-field weighting in Figure 2

We trim surrounding whitespace and give each distinct `Patch` field value a
total weight of one within its system. If `m` records share a field value, each
contributes `1/m` to its line-count bucket. The denominator is the number of
distinct field values (473 for Android, 492 for Linux, and 487 for HarmonyOS).

The full field stays together. In Linux, 44 records contain multiple URLs in
the field, and in HarmonyOS, six do. Counting individual URLs after splitting
those fields gives 616 distinct URLs in Linux and 494 in HarmonyOS.

Nine Android records point to the same Bluetooth commit. All nine report
33 changed lines, so they add 9 to the `30–50` bucket by record count and
1 after weighting.
[Android Bluetooth commit](https://android.googlesource.com/platform/packages/modules/Bluetooth/+/806774b1cf641e0c0e7df8024e327febf23d7d7c)

The `0–10` line bucket still has the largest share in all three systems. The
biggest change is Android's `30–50` bucket, from 15.00% to 13.74%, a drop of
1.26 percentage points.
[`patch_link_weighting.csv`](results/patch_link_weighting.csv)

## Re-running

`make extension` runs all three scripts and writes to `extension/results/`.
The first two scripts also accept `--out-dir`.
