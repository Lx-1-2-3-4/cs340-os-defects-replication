# AI usage statement

The course report requires an AI usage statement.  This page states, for the
layer-composition analysis and the verification track, what was produced with AI
assistance and what was done by the student.

## What AI assistance was used for

* Drafting the analysis code in `scripts/layer_analysis.py`,
  `scripts/run_layer_triplicate.py`, `scripts/crosscheck.py` and
  `scripts/extension.py`, and the unit tests in `tests/test_layer_rules.py`.
* Drafting the English text in `docs/METHODS.md`, `DEVIATIONS.md`,
  `MEMBER_CONTRIBUTION.md`, `GROUP_INTEGRATION.md`, `LAYER_ANALYSIS.md`,
  `LAYER_ONE_PAGER.md` and `results/REPORT.md`.
* Suggesting the analysis design (support rule, two weight sets, before/after
  distance decomposition) during a discussion of the assigned question.

## What the student did

* Set the scope from the group's task split and checked the design against the
  paper (Table II, Tables III–V, Figure 4).
* Ran every script, re-ran the three-run determinism check, and confirmed the
  unit tests pass.
* Checked the numbers in the tables against the generated CSVs and against the
  paper's definitions; rejected one earlier draft that clipped negative
  "explained" values, because the negative values are the finding.
* Reviewed and edited all English text before it entered the group report.

## Boundaries

* No data was generated, altered or invented; all inputs are the authors'
  released records (`../data/`, hashed in `PROVENANCE.json`).
* No result was reported without a reproducing script in this directory.
* AI tools had no access to the paper's unpublished material and did not
  re-label any patch.
* The paper values compared against are the group's transcription
  (`../data/paper/`), not an independent re-reading of the PDF by the AI.

## Verification

Every number in the write-up can be regenerated with:

```bash
python scripts/layer_analysis.py
python scripts/run_layer_triplicate.py
python -m unittest discover -s tests
```
