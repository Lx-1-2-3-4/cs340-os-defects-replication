"""Check the result files against the expected shape of the replication.

This is a self-test, not a comparison with the paper: it checks that every
printed value was recomputed (603), that 600 of them match, and that the three
exceptions are exactly the Figure 4d coefficients.

Usage:
    python scripts/validate.py
"""

from __future__ import annotations

import json
import sys

import common as C

EXPECTED_VALUES = {"table2": 114, "table3": 144, "table4": 126, "table5": 168,
                   "fig2": 15, "fig3": 24, "fig4": 12}
EXPECTED_TOTAL = 603
EXPECTED_MATCHED = 600


def main():
    check_path = C.RESULTS_DIR / "check.json"
    if not check_path.is_file():
        print("run scripts/reproduce.py and scripts/compare.py first")
        return 1
    check = json.loads(check_path.read_text(encoding="utf-8"))

    problems = []
    for item, expected in EXPECTED_VALUES.items():
        got = check["per_item"][item]["values"]
        if got != expected:
            problems.append(f"{item}: {got} values, expected {expected}")

    total = check["total"]
    if total["values"] != EXPECTED_TOTAL:
        problems.append(f"total values {total['values']}, expected {EXPECTED_TOTAL}")
    if total["matched"] != EXPECTED_MATCHED:
        problems.append(f"matched {total['matched']}, expected {EXPECTED_MATCHED}")

    rows = C.read_rows(C.RESULTS_DIR / "comparison.csv")
    mismatches = [r for r in rows if r["match"] != "yes"]
    if len(mismatches) != EXPECTED_TOTAL - EXPECTED_MATCHED:
        problems.append(f"{len(mismatches)} mismatches, expected 3")
    for row in mismatches:
        if not (row["item"] == "fig4" and row["key"].startswith("d_overall")):
            problems.append(f"unexpected mismatch: {row}")

    if problems:
        print("FAILED")
        for p in problems:
            print("  -", p)
        return 1
    print(f"OK: {total['values']} values, {total['matched']} matches, "
          "the 3 exceptions are Figure 4d")
    return 0


if __name__ == "__main__":
    sys.exit(main())
