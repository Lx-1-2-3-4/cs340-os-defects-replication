"""Recompute every quantitative value printed in Table II-V and Figure 2-4.

Usage:
    python scripts/reproduce.py [--data DIR] [--results DIR]

The output is one CSV per paper item plus summary.json.  Comparison with the
paper's printed values is a separate step (scripts/compare.py) so that the two
halves stay independent.
"""

from __future__ import annotations

import argparse
import sys

import common as C


def build_table2(data):
    counts = {panel: C.panel_counts(data, panel) for panel in C.TABLE2_PANELS}
    rows = []
    for panel in C.TABLE2_PANELS:
        for system in C.SYSTEMS:
            for category in C.CATEGORY_ORDER[panel]:
                n = counts[panel][system].get(category, 0)
                rows.append({"panel": panel, "os": system, "category": category,
                             "count": n, "our_pct": C.pct(n)})
    return rows


def build_joint(data, row_field, row_table, col_field, col_table,
                row_order, col_order, row_key, col_key):
    counts = C.joint_counts(data, row_field, row_table, col_field, col_table)
    rows = []
    for system in C.SYSTEMS:
        for r in row_order:
            for c in col_order:
                n = counts[system].get((r, c), 0)
                rows.append({"os": system, row_key: r, col_key: c,
                             "count": n, "our_pct": C.pct(n)})
    return rows


def build_table3(data):
    return build_joint(data, "OS Layer", C.LAYER, "Affected Function", C.FUNCTION,
                       C.LAYER_ROWS, C.FUNCTION_ROWS,
                       "row_layer", "col_function")


def build_table4(data):
    return build_joint(data, "OS Layer", C.LAYER, "Trigger Scenario", C.TRIGGER,
                       C.LAYER_ROWS, C.TRIGGER_COLUMNS,
                       "row_layer", "col_trigger")


def build_table5(data):
    return build_joint(data, "Affected Function", C.FUNCTION,
                       "Trigger Scenario", C.TRIGGER,
                       C.FUNCTION_ROWS, C.TRIGGER_COLUMNS,
                       "row_function", "col_trigger")


def build_histogram(data, field, buckets):
    counts = C.histogram_counts(data, field, buckets)
    rows = []
    for system in C.SYSTEMS:
        for name, _, _ in buckets:
            n = counts[system].get(name, 0)
            rows.append({"os": system, "bucket": name, "count": n,
                         "our_pct": C.pct(n)})
    return rows


def build_fig3(data):
    rows = []
    for metric, field in (("functions", "Involved Functions"),
                          ("files", "Modified Files")):
        for row in build_histogram(data, field, C.FIG3_BUCKETS):
            rows.append({"os": row["os"], "metric": metric,
                         "bucket": row["bucket"], "count": row["count"],
                         "our_pct": row["our_pct"]})
    return rows


def build_fig4(data):
    """Spearman coefficients of the four heatmap panels."""
    counts = {panel: C.panel_counts(data, panel) for panel in C.TABLE2_PANELS}
    vectors = {(panel, system): C.panel_vector(counts, panel, system)
               for panel in C.TABLE2_PANELS for system in C.SYSTEMS}

    rows = []
    for panel in ("a_os_layer", "b_affected_function", "c_trigger_scenario"):
        key = panel[2:]                      # a_os_layer -> os_layer
        for left, right in C.PAIRS:
            x, y = vectors[(key, left)], vectors[(key, right)]
            x, y = C.drop_double_zero(x, y)
            rows.append({"panel": panel, "pair": f"{left}-{right}",
                         "our_rho": round(C.spearman(x, y), 2)})

    # Panel (d) concatenates the 21 categories of panels (a)-(c).
    joined = {}
    for system in C.SYSTEMS:
        vec = []
        for key in ("os_layer", "affected_function", "trigger_scenario"):
            vec.extend(vectors[(key, system)])
        joined[system] = vec
    for left, right in C.PAIRS:
        x, y = C.drop_double_zero(joined[left], joined[right])
        rows.append({"panel": "d_overall", "pair": f"{left}-{right}",
                     "our_rho": round(C.spearman(x, y), 2)})
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default=str(C.DATA_DIR))
    parser.add_argument("--results", default=str(C.RESULTS_DIR))
    args = parser.parse_args(argv)

    data = C.load_dataset(args.data)
    out = C.Path(args.results)
    out.mkdir(parents=True, exist_ok=True)

    tables = {
        "table2": (build_table2(data),
                   ["panel", "os", "category", "count", "our_pct"]),
        "table3": (build_table3(data),
                   ["os", "row_layer", "col_function", "count", "our_pct"]),
        "table4": (build_table4(data),
                   ["os", "row_layer", "col_trigger", "count", "our_pct"]),
        "table5": (build_table5(data),
                   ["os", "row_function", "col_trigger", "count", "our_pct"]),
        "fig2": (build_histogram(data, "Line Changes", C.FIG2_BUCKETS),
                 ["os", "bucket", "count", "our_pct"]),
        "fig3": (build_fig3(data),
                 ["os", "metric", "bucket", "count", "our_pct"]),
        "fig4": (build_fig4(data), ["panel", "pair", "our_rho"]),
    }

    total = 0
    for name, (rows, fields) in tables.items():
        C.write_rows(out / f"{name}.csv", fields, rows)
        total += len(rows)
        print(f"  {name:7s} {len(rows):4d} values")

    C.write_json(out / "summary.json", {
        "values_recomputed": total,
        "dataset": C.data_hashes(args.data),
        "environment": C.environment(),
    })
    print(f"recomputed {total} values -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
