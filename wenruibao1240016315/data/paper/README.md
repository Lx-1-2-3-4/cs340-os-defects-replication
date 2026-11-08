# Machine-readable copies of the paper's values

These files are the reference values this replication compares against.  They
were transcribed from the arXiv HTML version of the paper
(<https://arxiv.org/html/2608.20643v1>) and from the figure assets, so the
comparison can run offline.

## Files

| File | Source in the paper | Method |
| --- | --- | --- |
| `table2.csv` | Table II, five panels | Parsed from the arXiv HTML table |
| `table3.csv` | Table III, OS layer × affected function | Parsed from the arXiv HTML table |
| `table4.csv` | Table IV, OS layer × trigger scenario | Parsed from the arXiv HTML table |
| `table5.csv` | Table V, affected function × trigger scenario | Parsed from the arXiv HTML table |
| `fig2.csv` | Figure 2, changed code lines | Read from the printed bar labels of `group_changes.png` |
| `fig3.csv` | Figure 3, involved functions / modified files | Read from the printed bar labels of `group_funcs.png` |
| `fig4.csv` | Figure 4, four similarity heatmaps | Read from the printed coefficients of `heatmap-a.png` … `heatmap-d.png` |

## Conventions

* Percentages keep the two decimals printed in the paper (`38.80` means 38.80 %).
* Cells left blank in the paper (zero values omitted for readability in
  Tables III–V) are stored as `0.00`.
* Figure 2 buckets are half-open: `[0,10) [10,30) [30,50) [50,100) [100,500]`;
  Figure 3 buckets are `[0,3) [3,5) [5,10) [10,50]`.  These boundaries are
  inferred: they reproduce all 39 printed percentages.
* Figure 4 heatmaps are symmetric, with rows and columns ordered Android,
  HarmonyOS, Linux.  Each unordered pair is stored once as `android-linux`,
  `android-harmony` or `linux-harmony`.
* Panel names in `fig4.csv` are `a_os_layer`, `b_affected_function`,
  `c_trigger_scenario`, `d_overall`.

## CSV schemas

```
table2.csv : panel, os, category, paper_pct
table3.csv : os, row_layer, col_function, paper_pct
table4.csv : os, row_layer, col_trigger, paper_pct
table5.csv : os, row_function, col_trigger, paper_pct
fig2.csv   : os, bucket, paper_pct
fig3.csv   : os, metric, bucket, paper_pct        # metric = functions | files
fig4.csv   : panel, pair, paper_rho
```

`os` is `android`, `linux` or `harmony`.

## Known inconsistency in the paper

The Figure 4d heatmap prints Android–HarmonyOS = −0.11, Android–Linux = 0.05 and
HarmonyOS–Linux = −0.04, while the text discussing the panel attributes −0.11 to
“Linux and Android”.  The transcription follows the heatmap, which is the value
this replication compares against; the inconsistency is analysed in
`../../docs/DISCREPANCIES.md`.
