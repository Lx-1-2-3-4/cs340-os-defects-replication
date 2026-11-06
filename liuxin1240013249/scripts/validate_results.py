#!/usr/bin/env python3
"""Compare the generated summary with the committed expectation.

``results/expected_summary.json`` records the match counts the committed dataset
must produce, so a silent change to the data or to the analysis code shows up
here:

    python scripts/validate_results.py

Exit code 0 means the summary matches the expectation exactly.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402  (local module, path set above)

COMPARED_FIELDS = (
    "total_values",
    "matched_values",
    "match_rate_pct",
    "mismatch_count",
    "checks",
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", default=str(common.DEFAULT_RESULTS_DIR))
    args = parser.parse_args(argv)
    results_dir = Path(args.results_dir)

    summary_path = results_dir / "summary.json"
    expected_path = results_dir / "expected_summary.json"
    for path in (summary_path, expected_path):
        if not path.exists():
            raise SystemExit(f"missing {path}; run `python scripts/run_triplicate.py` first")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    expected = json.loads(expected_path.read_text(encoding="utf-8"))

    problems = []
    for field in COMPARED_FIELDS:
        actual = summary.get(field)
        wanted = expected.get(field)
        if actual != wanted:
            problems.append(f"{field}: expected {wanted!r}, got {actual!r}")

    if problems:
        print("VALIDATION FAILED")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print("validation passed: reproduction summary matches expected_summary.json")
    print(f"  total values : {summary['total_values']}")
    print(f"  matched      : {summary['matched_values']} "
          f"({summary['match_rate_pct']:.2f}%)")
    print(f"  mismatches   : {summary['mismatch_count']} "
          f"(all in Figure 4 panel d; see docs/DISCREPANCIES.md)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
