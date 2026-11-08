"""Compare the recomputed values with the numbers printed in the paper.

Usage:
    python scripts/compare.py [--results DIR] [--paper DIR]

Reads the CSVs written by reproduce.py and the transcribed paper values in
data/paper/, then writes results/comparison.csv (one row per printed value) and
results/check.json (totals per item).
"""

from __future__ import annotations

import argparse
import sys

import common as C

KEYS = {
    "table2": ("panel", "os", "category"),
    "table3": ("os", "row_layer", "col_function"),
    "table4": ("os", "row_layer", "col_trigger"),
    "table5": ("os", "row_function", "col_trigger"),
    "fig2": ("os", "bucket"),
    "fig3": ("os", "metric", "bucket"),
    "fig4": ("panel", "pair"),
}
VALUE = {"fig4": "paper_rho", "default": "paper_pct"}
OURS = {"fig4": "our_rho", "default": "our_pct"}


def key_of(row, fields):
    return tuple(row[f] for f in fields)


def load_paper(paper_dir):
    paper_dir = C.Path(paper_dir)
    return {item: C.read_rows(paper_dir / f"{item}.csv") for item in KEYS}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", default=str(C.RESULTS_DIR))
    parser.add_argument("--paper", default=str(C.PAPER_DIR))
    parser.add_argument("--out", default=None)
    args = parser.parse_args(argv)

    results_dir = C.Path(args.results)
    out_dir = C.Path(args.out) if args.out else results_dir
    paper = load_paper(args.paper)

    rows = []
    per_item = {}
    for item, fields in KEYS.items():
        ours = {key_of(r, fields): r for r in C.read_rows(results_dir / f"{item}.csv")}
        value_field = VALUE.get(item, VALUE["default"])
        our_field = OURS.get(item, OURS["default"])
        matched = 0
        for paper_row in paper[item]:
            key = key_of(paper_row, fields)
            if key not in ours:
                raise KeyError(f"{item}: {key} missing from our results")
            mine = ours[key]
            paper_value = round(float(paper_row[value_field]), 2)
            our_value = round(float(mine[our_field]), 2)
            same = abs(paper_value - our_value) < 1e-9
            matched += same
            rows.append({
                "item": item,
                "key": "|".join(key),
                "paper": f"{paper_value:.2f}",
                "ours": f"{our_value:.2f}",
                "count": mine.get("count", ""),
                "match": "yes" if same else "NO",
            })
        per_item[item] = {"values": len(paper[item]), "matched": matched}

    total_values = sum(v["values"] for v in per_item.values())
    total_matched = sum(v["matched"] for v in per_item.values())

    C.write_rows(out_dir / "comparison.csv",
                 ["item", "key", "paper", "ours", "count", "match"], rows)
    C.write_json(out_dir / "check.json", {
        "per_item": per_item,
        "total": {"values": total_values, "matched": total_matched},
    })

    print(f"paper values compared : {total_values}")
    print(f"exact matches         : {total_matched}")
    for item, stats in per_item.items():
        flag = "ok" if stats["matched"] == stats["values"] else "MISMATCH"
        print(f"  {item:7s} {stats['matched']:4d}/{stats['values']:<4d} {flag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


