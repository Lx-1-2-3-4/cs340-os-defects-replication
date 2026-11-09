# Figure 4(a-c): uncertainty in cross-OS defect-profile correlations

## Argument and replication

The paper's Figure 4 and Finding 5 argue that defect-category profiles
differ across Android, Linux, and HarmonyOS. The existing reproduction
already matches all nine printed Spearman coefficients in panels (a)-(c).
This experiment adds record-level uncertainty intervals for those same
coefficients; it does not re-run the paper's Figure 4(d) analysis.

The experiment independently resamples 500 defect records with replacement
within each OS. For every replicate, it rebuilds the OS-layer, affected-
function, and trigger-scenario counts from the same sampled records, then
computes Spearman's rho for each OS pair. Categories that are zero in both
OS samples are dropped, following the existing Figure 4 reproduction rule.
The reported intervals are the 2.5th and 97.5th empirical percentiles.
The two stability columns show how often a replicate keeps the observed
sign and how often its absolute correlation is below the paper's 0.4
weak-correlation boundary.

## Results

| Figure panel | OS pair | Categories | Paper rho | Recomputed rho | 95% bootstrap interval | Same sign | \|rho\| < 0.4 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| OS layer | Android–Linux | 6 | 0.26 | 0.26 | [-0.30, 0.54] | 94.3% | 76.1% |
| OS layer | Android–HarmonyOS | 6 | -0.66 | -0.66 | [-0.89, -0.26] | 99.7% | 8.1% |
| OS layer | Linux–HarmonyOS | 6 | 0.09 | 0.09 | [-0.26, 0.31] | 62.7% | 98.8% |
| Affected function | Android–Linux | 8 | -0.19 | -0.19 | [-0.38, 0.14] | 86.3% | 98.4% |
| Affected function | Android–HarmonyOS | 8 | 0.43 | 0.43 | [0.10, 0.69] | 99.4% | 45.8% |
| Affected function | Linux–HarmonyOS | 8 | -0.52 | -0.52 | [-0.60, -0.19] | 99.9% | 43.1% |
| Trigger scenario | Android–Linux | 7 | 0.21 | 0.21 | [-0.41, 0.32] | 62.2% | 97.4% |
| Trigger scenario | Android–HarmonyOS | 6 | 0.38 | 0.38 | [0.09, 0.60] | 98.0% | 54.7% |
| Trigger scenario | Linux–HarmonyOS | 7 | 0.41 | 0.41 | [-0.09, 0.50] | 81.0% | 68.1% |

## Interpretation and limits

The original point estimates reproduce 9/9 exactly to the
paper's two-decimal precision. The intervals describe sensitivity of the
released 500-record samples to record resampling. They are not population-
level confidence intervals: the paper selected the latest 500 records per
OS rather than drawing a probability sample, and each rho is calculated
across only 6-8 fixed taxonomy categories. These results can show whether
the reported category ranking is stable under this resampling scheme, but
cannot establish that the same correlations hold for all OS defects.

Settings: 10,000 bootstrap replicates; seed 20261109; 500 records per OS;
Python 3.12.4; percentile interval; category order and shared-zero
rule inherited from scripts/common.py. Sampling uses the stable random.Random.random() stream.

Input SHA-256 (from the committed dataset snapshot):
- defects_android.json: a7fff6ef6ab1474d31a1c247e68d3818382e1f095ebd29e09e8443c4f7513be1
- defects_harmony.json: 49c36edbe9c1ff44d2e6b5218d37bfdc328af70e0decc3fb7738b20e109f2b69
- defects_linux.json: a21079dee00f037ed3d6b42ae458422b78e4ba1b1fc933f1fb7518953754f2ee

Run from the member folder with python extension/figure4_bootstrap.py.
The script writes this report and figure4_bootstrap.csv under
extension/results/.
