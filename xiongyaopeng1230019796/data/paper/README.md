# Machine-readable copies of the paper's values

The files in this directory are the reference values the reproduction is compared
against. They are transcribed from the arXiv HTML version
(<https://arxiv.org/html/2608.20643v1>) so the comparison can run offline.

## How the values were transcribed

| File | Source in the paper | Method |
| --- | --- | --- |
| `table2.csv` | Table II (five panels: OS layer, affected function, trigger scenario, severity, repaired code elements) | Parsed from the arXiv HTML table. A transcription typo would show up as a mismatch in the reproduction. |
| `table3.csv` | Table III (OS layer × affected function) | Parsed from the arXiv HTML table; the joint tables list columns in alphabetical order, different from Table II, and the transcription keeps the table's own order. |
| `table4.csv` | Table IV (OS layer × trigger scenario) | Same as Table III. |
| `table5.csv` | Table V (affected function × trigger scenario) | Same as Table III. |
| `fig2.csv` | Figure 2 (line changes distribution) | Read from the arXiv figure asset (`group_changes.png`), which prints every percentage as a bar label. |
| `fig3.csv` | Figure 3 (involved functions / modified files) | Read from the arXiv figure asset (`group_funcs.png`), which prints every percentage as a bar label. |
| `fig4.csv` | Figure 4 (similarity heatmaps) | Read from the four arXiv heatmap assets (`heatmap-a.png` … `heatmap-d.png`); the printed coefficients are two-decimal numbers. |

In total 603 reference values are compared with the recomputation; 600 match
exactly (`results/SUMMARY.md`). The 3 that do not match are exactly the three
coefficients of Figure 4d and are analysed in `docs/DISCREPANCIES.md`.

## Conventions

* All percentages are stored as decimal numbers with two fractional digits as
  printed in the paper (e.g. `38.80` means 38.80%).
* Cells rendered as blank in the paper (zero omitted for readability, as stated
  in the Table III–V captions) are stored as `0.00`.
* Figure 2 buckets are half-open intervals: `[0,10)`, `[10,30)`, `[30,50)`,
  `[50,100)`, `[100,500]`. Figure 3 buckets are `[0,3)`, `[3,5)`, `[5,10)`,
  `[10,50]`. These boundary rules are inferred from the data: they reproduce all
  15 Figure 2 and all 24 Figure 3 percentages exactly.
* Figure 4 heatmaps are symmetric; the printed matrix has rows and columns in
  the order `Android`, `HarmonyOS`, `Linux`. The CSV stores each unordered pair
  once, as `android-linux`, `android-harmony` and `linux-harmony`.
* Panel names in `fig4.csv`: `a_os_layer`, `b_affected_function`,
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

`os` is always one of `android`, `linux`, `harmony`. `panel` in `table2.csv` is
one of `os_layer`, `affected_function`, `trigger_scenario`, `severity`,
`code_element`.

## Known inconsistency in the paper

The Figure 4d heatmap shows `Android–HarmonyOS = -0.11`, `Android–Linux = 0.05`
and `HarmonyOS–Linux = -0.04`, while the Figure 4d discussion text attributes the
`-0.11` coefficient to "Linux and Android". The transcription follows the figure,
which is what the reproduction compares against. This internal inconsistency is
one of the findings discussed in `docs/DISCREPANCIES.md`.
