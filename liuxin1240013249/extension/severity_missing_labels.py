#!/usr/bin/env python3
"""Extension 2 (secondary): what happens if missing severity labels are excluded?

Table II reports severity distributions in which 65.20% of the Linux defects
and 1.20% of the HarmonyOS defects fall into "Undecided"/"Unknown", so the
cross-OS severity comparison is driven partly by missing data on Linux. This
experiment changes one factor, how missing severity labels are counted, and
recomputes the shares.

Missing labels are kept as a category (the paper's treatment) or removed from
the denominator; everything else stays the same. The outputs are the per-OS
category shares under both treatments, the top category in each case, and the
change of each share.

Outputs: extension/results/severity_missing_labels.csv and .md.

Usage
-----
    python extension/severity_missing_labels.py
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import common  # noqa: E402  (path set above)

MISSING = "Undecided"


def top_category(counts, order):
    """Most frequent category, ties broken by the paper's column order."""
    best, best_key = None, None
    for index, category in enumerate(order):
        key = (counts.get(category, 0), -index)
        if best_key is None or key > best_key:
            best, best_key = category, key
    return best


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-dir", default=str(common.DEFAULT_DATA_DIR))
    parser.add_argument("--out-dir", default=str(REPO_ROOT / "extension" / "results"))
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    records = common.load_defects(args.data_dir)
    order = common.PANEL_COLUMNS["severity"]

    rows = []
    os_summary = {}
    for tag in common.OS_TAGS:
        rows_for_os = records[tag]
        total = len(rows_for_os)
        counts = Counter(common.SEVERITY_LABEL[row["Severity Level"]] for row in rows_for_os)
        missing = counts.get(MISSING, 0)
        labeled_total = total - missing
        top_with_missing = top_category(counts, order)
        labeled_counts = Counter({category: counts.get(category, 0) for category in order
                                  if category != MISSING})
        top_labeled = top_category(labeled_counts, order)
        os_summary[tag] = {
            "total": total,
            "missing": missing,
            "labeled_total": labeled_total,
            "top_with_missing": top_with_missing,
            "top_labeled": top_labeled,
        }
        for category in order:
            count = counts.get(category, 0)
            share_with = 100.0 * count / total
            if category == MISSING:
                share_without = None
                change = None
            else:
                share_without = 100.0 * count / labeled_total
                change = share_without - share_with
            rows.append({
                "os": tag,
                "category": category,
                "defects": count,
                "share_with_missing_pct": f"{share_with:.2f}",
                "share_labeled_only_pct": "" if share_without is None else f"{share_without:.2f}",
                "change_pp": "" if change is None else f"{change:+.2f}",
                "top_category_with_missing": top_with_missing,
                "top_category_labeled_only": top_labeled,
                "missing_defects": missing,
                "missing_share_pct": f"{100.0 * missing / total:.2f}",
            })
    common.write_csv(
        out_dir / "severity_missing_labels.csv",
        ["os", "category", "defects", "share_with_missing_pct", "share_labeled_only_pct",
         "change_pp", "top_category_with_missing", "top_category_labeled_only",
         "missing_defects", "missing_share_pct"],
        rows,
    )

    linux_high_with = next(row for row in rows
                           if row["os"] == "linux" and row["category"] == "High")
    harmony = os_summary["harmony"]
    android = os_summary["android"]
    lines = [
        "# Extension 2: missing severity labels",
        "",
        "The paper's severity comparison includes a large 'Undecided' category",
        f"(Linux {100.0 * os_summary['linux']['missing'] / os_summary['linux']['total']:.2f}%). This experiment",
        "removes it from the denominator and recomputes the shares, leaving the",
        "records and labels unchanged.",
        "",
        "## Top category under both treatments",
        "",
        "| OS | Missing labels | Top category (paper treatment) | Top category (labeled only) |",
        "| --- | ---: | --- | --- |",
    ]
    for tag in common.OS_TAGS:
        info = os_summary[tag]
        lines.append(
            f"| {common.OS_DISPLAY[tag]} | {info['missing']}/{info['total']} "
            f"({100.0 * info['missing'] / info['total']:.2f}%) | "
            f"{info['top_with_missing']} | {info['top_labeled']} |"
        )
    lines += [
        "",
        "Per-category shares under both treatments:",
        "",
        "| OS | Category | With missing (%) | Labeled only (%) | Change (pp) |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in rows:
        labeled = row["share_labeled_only_pct"] if row["share_labeled_only_pct"] else "n/a"
        change = row["change_pp"] if row["change_pp"] else "n/a"
        lines.append(
            f"| {common.OS_DISPLAY[row['os']]} | {row['category']} | "
            f"{row['share_with_missing_pct']} | {labeled} | {change} |"
        )
    lines += [
        "",
        "## What this says",
        "",
        f"Android has no missing labels, so nothing changes ({android['top_with_missing']} stays",
        "the most frequent severity). On Linux, dropping the missing records raises",
        f"High from {linux_high_with['share_with_missing_pct']}% to {linux_high_with['share_labeled_only_pct']}%",
        "and makes it the most frequent labelled severity; with the paper's treatment",
        f"the top category is {os_summary['linux']['top_with_missing']} instead. HarmonyOS has only",
        f"{harmony['missing']} missing records, too few to change the ranking "
        f"({harmony['top_with_missing']} remains first).",
        "",
        "So the cross-OS severity comparison in Table II is partly a comparison of",
        "label availability rather than of severity itself, and the Linux numbers",
        "should be read conditional on that.",
        "",
        "Numbers written by `extension/severity_missing_labels.py`.",
        "",
    ]
    common.write_text(out_dir / "severity_missing_labels.md", "\n".join(lines))
    print(f"wrote {out_dir / 'severity_missing_labels.csv'}")
    print(f"wrote {out_dir / 'severity_missing_labels.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
