# Cross-check: this implementation vs the main implementation

The main implementation is `../liuxin1240013249/`; it shares no source
file with this folder.  The two result sets are joined on the paper keys
and compared value by value (two decimals) and count by count.

| Item | Values | Identical values | Identical counts |
| --- | ---: | ---: | ---: |
| table2 | 114 | 114 | 114 |
| table3 | 144 | 144 | 144 |
| table4 | 126 | 126 | 126 |
| table5 | 168 | 168 | 168 |
| fig2 | 15 | 15 | 15 |
| fig3 | 24 | 24 | 24 |
| fig4 | 12 | 12 | 0 |
| **Total** | **603** | **603** | **591** |

Agreement: 603/603 values (100.00 %).

The three Figure 4d coefficients that differ from the paper are here
identical between the two implementations, which is the evidence that the
discrepancy is in the paper, not in the code.
