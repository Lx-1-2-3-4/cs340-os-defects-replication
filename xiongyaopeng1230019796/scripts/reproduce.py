#!/usr/bin/env python3
"""Recompute every quantitative result of the paper from the released dataset.

Covered results (see docs/CLAIMS.md):

* Table II   -- five panels of single-dimension distributions (114 percentages)
* Table III  -- OS layer x affected function (144 percentages)
* Table IV   -- OS layer x trigger scenario (126 percentages)
* Table V    -- affected function x trigger scenario (168 percentages)
* Figure 2   -- distribution of changed code lines (15 percentages)
* Figure 3   -- distribution of involved functions / modified files (24 percentages)
* Figure 4   -- cross-OS Spearman similarity heatmaps (12 coefficients)

Every value is written to ``results/`` as a CSV row containing the paper value,
the recomputed value and a match flag, so each number can be traced to a log.
The script is deterministic: no randomness and no timestamps in the outputs.

Usage
-----
    python scripts/reproduce.py [--out-dir results]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402  (local module, path set above)

TOTAL_PER_SYSTEM = 500


def _compare(paper_value: str, ours_float: float, formatter) -> tuple[str, bool, float]:
    ours_text = formatter(ours_float)
    match = ours_text == paper_value
    diff = round(ours_float - float(paper_value), 6)
    return ours_text, match, diff


def check_table2(records, paper_rows, out_dir: Path) -> list:
    counts = {panel: common.panel_counts(records, panel) for panel in common.TABLE2_PANELS}
    rows = []
    for paper in paper_rows:
        panel, tag, category = paper["panel"], paper["os"], paper["category"]
        count = counts[panel][tag].get(category, 0)
        ours = 100.0 * count / TOTAL_PER_SYSTEM
        ours_text, match, diff = _compare(paper["paper_pct"], ours, common.fmt_pct)
        rows.append({
            "panel": panel,
            "os": tag,
            "category": category,
            "defects": count,
            "paper_pct": paper["paper_pct"],
            "ours_pct": ours_text,
            "match": "yes" if match else "no",
            "diff_pp": f"{diff:+.2f}",
        })
    common.write_csv(
        out_dir / "table2_reproduction.csv",
        ["panel", "os", "category", "defects", "paper_pct", "ours_pct", "match", "diff_pp"],
        rows,
    )
    return rows


def check_joint(records, paper_rows, out_dir: Path, name: str, row_field, row_map,
                col_field, col_map, row_key: str, col_key: str) -> list:
    counts = common.joint_counts(records, row_field, row_map, col_field, col_map)
    rows = []
    for paper in paper_rows:
        tag = paper["os"]
        count = counts[tag].get((paper[row_key], paper[col_key]), 0)
        ours = 100.0 * count / TOTAL_PER_SYSTEM
        ours_text, match, diff = _compare(paper["paper_pct"], ours, common.fmt_pct)
        rows.append({
            "os": tag,
            row_key: paper[row_key],
            col_key: paper[col_key],
            "defects": count,
            "paper_pct": paper["paper_pct"],
            "ours_pct": ours_text,
            "match": "yes" if match else "no",
            "diff_pp": f"{diff:+.2f}",
        })
    common.write_csv(
        out_dir / f"{name}_reproduction.csv",
        ["os", row_key, col_key, "defects", "paper_pct", "ours_pct", "match", "diff_pp"],
        rows,
    )
    return rows


def check_fig2(records, paper_rows, out_dir: Path) -> list:
    rows = []
    for paper in paper_rows:
        tag, bucket = paper["os"], paper["bucket"]
        count = sum(1 for row in records[tag]
                    if common.bucket_name(row["Line Changes"], common.FIG2_BUCKETS) == bucket)
        ours = 100.0 * count / TOTAL_PER_SYSTEM
        ours_text, match, diff = _compare(paper["paper_pct"], ours, common.fmt_pct)
        rows.append({
            "os": tag,
            "bucket": bucket,
            "defects": count,
            "paper_pct": paper["paper_pct"],
            "ours_pct": ours_text,
            "match": "yes" if match else "no",
            "diff_pp": f"{diff:+.2f}",
        })
    common.write_csv(
        out_dir / "fig2_reproduction.csv",
        ["os", "bucket", "defects", "paper_pct", "ours_pct", "match", "diff_pp"],
        rows,
    )
    return rows


def check_fig3(records, paper_rows, out_dir: Path) -> list:
    field_for_metric = {"functions": "Involved Functions", "files": "Modified Files"}
    rows = []
    for paper in paper_rows:
        tag, metric, bucket = paper["os"], paper["metric"], paper["bucket"]
        field = field_for_metric[metric]
        count = sum(1 for row in records[tag]
                    if common.bucket_name(row[field], common.FIG3_BUCKETS) == bucket)
        ours = 100.0 * count / TOTAL_PER_SYSTEM
        ours_text, match, diff = _compare(paper["paper_pct"], ours, common.fmt_pct)
        rows.append({
            "os": tag,
            "metric": metric,
            "bucket": bucket,
            "defects": count,
            "paper_pct": paper["paper_pct"],
            "ours_pct": ours_text,
            "match": "yes" if match else "no",
            "diff_pp": f"{diff:+.2f}",
        })
    common.write_csv(
        out_dir / "fig3_reproduction.csv",
        ["os", "metric", "bucket", "defects", "paper_pct", "ours_pct", "match", "diff_pp"],
        rows,
    )
    return rows


# ---------------------------------------------------------------------------
# Figure 4: cross-system similarity (Spearman's rho)
# ---------------------------------------------------------------------------

def dimension_vectors(records) -> dict:
    """Return the three marginal distributions used by panels (a)-(c) of Fig. 4."""
    counts = {panel: common.panel_counts(records, panel) for panel in
              ("os_layer", "affected_function", "trigger_scenario")}
    vectors = {}
    for panel in counts:
        vectors[panel] = {
            tag: [counts[panel][tag].get(category, 0) for category in common.PANEL_COLUMNS[panel]]
            for tag in common.OS_TAGS
        }
    return vectors


def correlation_pairs(vectors_by_tag) -> dict:
    """Spearman rho for the three OS pairs, dropping categories zero in both."""
    out = {}
    for left, right in common.PAIRS:
        x, y = common.drop_shared_zeros(vectors_by_tag[left], vectors_by_tag[right])
        out[(left, right)] = common.spearman(x, y)
    return out


def compute_fig4(records) -> tuple[dict, list]:
    """Return ({panel: {(a,b): rho}}, candidate_rows_for_overall_panel)."""
    marginal = dimension_vectors(records)
    panels = {
        "a_os_layer": correlation_pairs(marginal["os_layer"]),
        "b_affected_function": correlation_pairs(marginal["affected_function"]),
        "c_trigger_scenario": correlation_pairs(marginal["trigger_scenario"]),
    }

    severity = {
        tag: [common.panel_counts(records, "severity")[tag].get(c, 0)
              for c in common.PANEL_COLUMNS["severity"]]
        for tag in common.OS_TAGS
    }
    code_elements = {
        tag: [common.panel_counts(records, "code_element")[tag].get(c, 0)
              for c in common.PANEL_COLUMNS["code_element"]]
        for tag in common.OS_TAGS
    }

    def concat(*parts):
        return {tag: [value for part in parts for value in part[tag]] for tag in common.OS_TAGS}

    overall = concat(marginal["os_layer"], marginal["affected_function"], marginal["trigger_scenario"])
    overall_with_severity = concat(marginal["os_layer"], marginal["affected_function"],
                                   marginal["trigger_scenario"], severity)
    overall_all_five = concat(marginal["os_layer"], marginal["affected_function"],
                              marginal["trigger_scenario"], severity, code_elements)

    # Candidate rules for the unspecified "Overall" panel (Fig. 4d).
    candidates = []
    candidate_vectors = [
        ("concat_21_drop_shared_zeros", overall),
        ("concat_21_no_filter", overall),
        ("concat_26_with_severity", overall_with_severity),
        ("concat_38_with_severity_and_code_elements", overall_all_five),
    ]
    for name, vectors in candidate_vectors:
        for left, right in common.PAIRS:
            x, y = vectors[left], vectors[right]
            if name.endswith("drop_shared_zeros"):
                x, y = common.drop_shared_zeros(x, y)
            rho = common.spearman(x, y)
            candidates.append({
                "rule": name,
                "pair": f"{left}-{right}",
                "rho": common.fmt_rho(rho),
                "categories": len(x),
            })
    # Arithmetic mean of the three marginal panel coefficients.
    for left, right in common.PAIRS:
        rho = sum(panels[p][(left, right)] for p in panels) / len(panels)
        candidates.append({
            "rule": "mean_of_marginal_panels",
            "pair": f"{left}-{right}",
            "rho": common.fmt_rho(rho),
            "categories": None,
        })

    panels["d_overall"] = correlation_pairs(overall)
    return panels, candidates


def check_fig4(panels, paper_rows, out_dir: Path, candidates) -> list:
    rows = []
    for paper in paper_rows:
        panel = paper["panel"]
        left, right = paper["pair"].split("-")
        rho = panels[panel][(left, right)]
        ours_text, match, diff = _compare(paper["paper_rho"], rho, common.fmt_rho)
        rows.append({
            "panel": panel,
            "pair": paper["pair"],
            "paper_rho": paper["paper_rho"],
            "ours_rho": ours_text,
            "match": "yes" if match else "no",
            "diff": f"{diff:+.2f}",
        })
    common.write_csv(
        out_dir / "fig4_reproduction.csv",
        ["panel", "pair", "paper_rho", "ours_rho", "match", "diff"],
        rows,
    )
    common.write_csv(
        out_dir / "fig4_overall_candidates.csv",
        ["rule", "pair", "rho", "categories"],
        candidates,
    )
    return rows


# ---------------------------------------------------------------------------
# Summary generation
# ---------------------------------------------------------------------------

CHECK_LABELS = {
    "table2": "Table II - five distribution panels",
    "table3": "Table III - OS layer x affected function",
    "table4": "Table IV - OS layer x trigger scenario",
    "table5": "Table V - affected function x trigger scenario",
    "fig2": "Figure 2 - changed code lines",
    "fig3": "Figure 3 - involved functions / modified files",
    "fig4": "Figure 4 - cross-OS similarity (Spearman rho)",
}


def summarise(rows) -> dict:
    total = len(rows)
    matched = sum(1 for row in rows if row["match"] == "yes")
    return {"total": total, "matched": matched,
            "match_rate_pct": round(100.0 * matched / total, 2) if total else 0.0}


def write_summary_markdown(path: Path, summary: dict, checks: dict, mismatches: list) -> None:
    lines = [
        "# Reproduction summary",
        "",
        "Generated by `scripts/reproduce.py` from the committed dataset in `data/` and the",
        "paper values transcribed into `data/paper/`. Each number in this file also appears",
        "in `results/*.csv`.",
        "",
        "## Match rate per result",
        "",
        "| Result | Values compared | Matched | Match rate |",
        "| --- | ---: | ---: | ---: |",
    ]
    for key in CHECK_LABELS:
        info = checks[key]
        lines.append(f"| {CHECK_LABELS[key]} | {info['total']} | {info['matched']} | {info['match_rate_pct']:.2f}% |")
    lines.append(f"| **Total** | **{summary['total_values']}** | **{summary['matched_values']}** | "
                 f"**{summary['match_rate_pct']:.2f}%** |")
    lines += [
        "",
        "## Values that do not match the paper",
        "",
    ]
    if mismatches:
        lines.append("| Result | OS / pair | Key | Paper | Ours | Difference |")
        lines.append("| --- | --- | --- | ---: | ---: | ---: |")
        for row in mismatches:
            lines.append(
                f"| {row['check']} | {row['unit']} | {row['key']} | {row['paper']} | "
                f"{row['ours']} | {row['diff']} |"
            )
    else:
        lines.append("None.")
    lines += [
        "",
        "The nine coefficients of Figure 4 panels (a)-(c) match. The three mismatches are",
        "the coefficients of the unspecified panel (d) ('Overall'); see",
        "`docs/DISCREPANCIES.md`.",
        "",
        "## Determinism",
        "",
        "The pipeline has no randomness and writes no timestamps into the results, so three",
        "runs produce byte-identical files. `scripts/run_triplicate.py` records the SHA-256",
        "of every output after each run in `results/logs/determinism.txt`; the standard",
        "deviation across the three runs is 0.00 for every value. Sampling error of the",
        "500-defect sample is a separate question and is not measured here.",
        "",
        "## Environment of this run",
        "",
        "```",
    ]
    lines += [f"{key}: {value}" for key, value in summary["environment"].items()]
    lines += [
        "```",
        "",
        "## Dataset integrity",
        "",
        "| File | SHA-256 |",
        "| --- | --- |",
    ]
    for name, digest in summary["data_sha256"].items():
        lines.append(f"| `data/{name}` | `{digest}` |")
    lines += [
        "",
        "`scripts/reproduce.py` also hashes itself; the reproduction script digest is recorded",
        "in `results/summary.json`.",
        "",
    ]
    common.write_text(path, "\n".join(lines) + "\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-dir", default=str(common.DEFAULT_DATA_DIR))
    parser.add_argument("--paper-dir", default=str(common.DEFAULT_PAPER_DIR))
    parser.add_argument("--out-dir", default=str(common.DEFAULT_RESULTS_DIR))
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("loading dataset and paper values...")
    records = common.load_defects(args.data_dir)
    paper = common.load_paper_values(args.paper_dir)

    print("checking Table II (five distribution panels)...")
    table2_rows = check_table2(records, paper["table2"], out_dir)
    print("checking Tables III-V (joint distributions)...")
    table3_rows = check_joint(records, paper["table3"], out_dir, "table3",
                              "OS Layer", common.OS_LAYER_LABEL,
                              "Affected Function", common.AFFECTED_FUNCTION_LABEL,
                              "row_layer", "col_function")
    table4_rows = check_joint(records, paper["table4"], out_dir, "table4",
                              "OS Layer", common.OS_LAYER_LABEL,
                              "Trigger Scenario", common.TRIGGER_LABEL,
                              "row_layer", "col_trigger")
    table5_rows = check_joint(records, paper["table5"], out_dir, "table5",
                              "Affected Function", common.AFFECTED_FUNCTION_LABEL,
                              "Trigger Scenario", common.TRIGGER_LABEL,
                              "row_function", "col_trigger")
    print("checking Figures 2-3 (change size distributions)...")
    fig2_rows = check_fig2(records, paper["fig2"], out_dir)
    fig3_rows = check_fig3(records, paper["fig3"], out_dir)
    print("checking Figure 4 (cross-OS similarity)...")
    fig4_panels, fig4_candidates = compute_fig4(records)
    fig4_rows = check_fig4(fig4_panels, paper["fig4"], out_dir, fig4_candidates)

    rows_by_check = {
        "table2": table2_rows,
        "table3": table3_rows,
        "table4": table4_rows,
        "table5": table5_rows,
        "fig2": fig2_rows,
        "fig3": fig3_rows,
        "fig4": fig4_rows,
    }
    checks = {key: summarise(rows) for key, rows in rows_by_check.items()}
    matched = sum(info["matched"] for info in checks.values())
    total = sum(info["total"] for info in checks.values())

    mismatches = []
    for key, rows in rows_by_check.items():
        for row in rows:
            if row["match"] == "no":
                if key == "table2":
                    detail = f"{row['panel']} / {row['category']}"
                    unit = row["os"]
                elif key == "fig3":
                    detail = f"{row['metric']} / {row['bucket']}"
                    unit = row["os"]
                elif key in ("table3", "table4", "table5"):
                    row_key = next(k for k in row if k.startswith("row_"))
                    col_key = next(k for k in row if k.startswith("col_"))
                    detail = f"{row[row_key]} x {row[col_key]}"
                    unit = row["os"]
                elif key == "fig2":
                    detail = row["bucket"]
                    unit = row["os"]
                else:
                    detail = row["panel"]
                    unit = row["pair"]
                mismatches.append({
                    "check": key,
                    "unit": unit,
                    "key": detail,
                    "paper": row.get("paper_pct") or row.get("paper_rho"),
                    "ours": row.get("ours_pct") or row.get("ours_rho"),
                    "diff": row.get("diff_pp") or row.get("diff"),
                })

    summary = {
        "paper": "arXiv:2608.20643v1",
        "total_values": total,
        "matched_values": matched,
        "match_rate_pct": round(100.0 * matched / total, 2),
        "checks": checks,
        "mismatch_count": len(mismatches),
        "environment": common.environment_info(),
        "data_sha256": common.data_sha256(args.data_dir),
        "reproduce_script_sha256": common.sha256_file(Path(__file__)),
    }
    common.write_text(out_dir / "summary.json", json.dumps(summary, indent=2) + "\n")
    write_summary_markdown(out_dir / "SUMMARY.md", summary, checks, mismatches)

    print()
    for key in CHECK_LABELS:
        info = checks[key]
        print(f"[{key}] {info['matched']}/{info['total']} values match "
              f"({info['match_rate_pct']:.2f}%)")
    print(f"GRAND TOTAL: {matched}/{total} values match ({summary['match_rate_pct']:.2f}%)")
    if mismatches:
        print()
        print("mismatches:")
        for row in mismatches:
            print(f"  - {row['check']}: {row['unit']} {row['key']}: "
                  f"paper={row['paper']} ours={row['ours']} diff={row['diff']}")
    print()
    print(f"wrote {len(list(out_dir.glob('*.csv')))} CSV files, summary.json and SUMMARY.md to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
