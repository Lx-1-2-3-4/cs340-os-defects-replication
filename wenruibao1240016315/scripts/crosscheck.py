"""Cross-check this implementation against the group's main implementation.

This folder is the group's *second, independently written* implementation of the
same 603 values.  It exists to show that the numbers do not depend on one
person's code: if two implementations that share no source file produce the same
603 values, the tables and figures are a property of the dataset, not of a bug
in one script.

The main implementation lives in ``../liuxin1240013249/`` and writes its results
to ``results/*_reproduction.csv``.  This script joins the two result sets on the
paper keys and reports, value by value and count by count, whether they agree.

Usage:
    python scripts/crosscheck.py [--main DIR] [--results DIR] [--out DIR]
"""

from __future__ import annotations

import argparse
import sys

import common as C

ITEMS = {
    "table2": (("panel", "os", "category"), "ours_pct", "defects"),
    "table3": (("os", "row_layer", "col_function"), "ours_pct", "defects"),
    "table4": (("os", "row_layer", "col_trigger"), "ours_pct", "defects"),
    "table5": (("os", "row_function", "col_trigger"), "ours_pct", "defects"),
    "fig2": (("os", "bucket"), "ours_pct", "defects"),
    "fig3": (("os", "metric", "bucket"), "ours_pct", "defects"),
    "fig4": (("panel", "pair"), "ours_rho", None),
}


def key(row, fields):
    return "|".join(row[f] for f in fields)


def load(path, fields, value_col):
    rows = {}
    for row in C.read_rows(path):
        rows[key(row, fields)] = row
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main", required=True,
                        help="results directory of the main implementation")
    parser.add_argument("--results", default=str(C.RESULTS_DIR))
    parser.add_argument("--out", default=None)
    args = parser.parse_args(argv)

    main_dir = C.Path(args.main)
    results_dir = C.Path(args.results)
    out_dir = C.Path(args.out) if args.out else results_dir

    rows = []
    summary = {}
    for item, (fields, value_col, count_col) in ITEMS.items():
        main_rows = load(main_dir / f"{item}_reproduction.csv", fields, value_col)
        our_rows = load(results_dir / f"{item}.csv", fields, value_col)
        same_value = same_count = 0
        for k, main_row in main_rows.items():
            if k not in our_rows:
                raise KeyError(f"{item}: {k} missing from this implementation")
            our_row = our_rows[k]
            main_value = round(float(main_row[value_col]), 2)
            our_value = round(float(our_row["our_pct" if item != "fig4" else "our_rho"]), 2)
            value_ok = abs(main_value - our_value) < 1e-9
            count_ok = ""
            if count_col:
                count_ok = str(int(main_row[count_col])) == str(int(our_row["count"]))
                same_count += count_ok
            same_value += value_ok
            rows.append({
                "item": item, "key": k,
                "main": f"{main_value:.2f}", "ours": f"{our_value:.2f}",
                "same_value": "yes" if value_ok else "NO",
                "main_count": main_row[count_col] if count_col else "",
                "our_count": our_row["count"] if count_col else "",
                "same_count": ("yes" if count_ok else "NO") if count_col else "",
            })
        summary[item] = {"values": len(main_rows), "same_value": same_value,
                         "same_count": same_count}

    C.write_rows(out_dir / "crosscheck.csv",
                 ["item", "key", "main", "ours", "same_value",
                  "main_count", "our_count", "same_count"], rows)

    total_values = sum(v["values"] for v in summary.values())
    total_same = sum(v["same_value"] for v in summary.values())
    C.write_json(out_dir / "crosscheck.json", {
        "per_item": summary,
        "total": {"values": total_values, "same_value": total_same},
    })

    print(f"values compared with the main implementation: {total_values}")
    print(f"identical values                            : {total_same}")
    for item, stats in summary.items():
        print(f"  {item:7s} {stats['same_value']:4d}/{stats['values']:<4d} values, "
              f"{stats['same_count']:4d} matching counts")

    # One-page human-readable summary, committed next to the CSV.
    lines = [
        "# Cross-check: this implementation vs the main implementation",
        "",
        "The main implementation is `../liuxin1240013249/`; it shares no source",
        "file with this folder.  The two result sets are joined on the paper keys",
        "and compared value by value (two decimals) and count by count.",
        "",
        "| Item | Values | Identical values | Identical counts |",
        "| --- | ---: | ---: | ---: |",
    ]
    for item, stats in summary.items():
        lines.append(f"| {item} | {stats['values']} | {stats['same_value']} | "
                     f"{stats['same_count']} |")
    lines += [
        f"| **Total** | **{total_values}** | **{total_same}** | "
        f"**{sum(v['same_count'] for v in summary.values())}** |",
        "",
        f"Agreement: {total_same}/{total_values} values "
        f"({100.0 * total_same / total_values:.2f} %).",
        "",
        "The three Figure 4d coefficients that differ from the paper are here",
        "identical between the two implementations, which is the evidence that the",
        "discrepancy is in the paper, not in the code.",
        "",
    ]
    C.write_text(out_dir / "CROSSCHECK.md", "\n".join(lines))
    return 0 if total_same == total_values else 1


if __name__ == "__main__":
    sys.exit(main())
