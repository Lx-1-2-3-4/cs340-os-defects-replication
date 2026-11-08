# Determinism check

3 independent runs of reproduce.py + compare.py.

| file | run1 | run2 | run3 | identical |
| --- | --- | --- | --- | --- |
| table2.csv | 3880860cee79 | 3880860cee79 | 3880860cee79 | yes |
| table3.csv | 6937383a6ccf | 6937383a6ccf | 6937383a6ccf | yes |
| table4.csv | 2548c1e4a55d | 2548c1e4a55d | 2548c1e4a55d | yes |
| table5.csv | cc436ff78435 | cc436ff78435 | cc436ff78435 | yes |
| fig2.csv | 557a1fd93687 | 557a1fd93687 | 557a1fd93687 | yes |
| fig3.csv | 93991458e59f | 93991458e59f | 93991458e59f | yes |
| fig4.csv | 403a02be17a8 | 403a02be17a8 | 403a02be17a8 | yes |
| comparison.csv | 0529a683d572 | 0529a683d572 | 0529a683d572 | yes |
| check.json | 3e300b85be4e | 3e300b85be4e | 3e300b85be4e | yes |

All outputs identical across 3 runs: yes.
