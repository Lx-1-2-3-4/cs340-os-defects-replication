"""Generate genuine SVG charts and an English report without plotting packages."""
from __future__ import annotations
import argparse
import html
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import core as C

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
BLUE, ORANGE, INK = "#2463a6", "#b85416", "#18283b"
PANEL_NAMES = {"a_os_layer": "OS layer", "b_affected_function": "Affected function", "c_trigger_scenario": "Trigger scenario"}


def element(parent, kind, attrs=None, content=None):
    node = ET.SubElement(parent, f"{{{NS}}}{kind}", {k.replace("_", "-"): str(v) for k, v in (attrs or {}).items()})
    if content is not None:
        node.text = str(content)
    return node


def label(parent, x, y, content, size=14, color=INK, anchor="start", **extra):
    return element(parent, "text", {"x": x, "y": y, "font_size": size, "fill": color, "text_anchor": anchor, **extra}, content)


def canvas(title, subtitle, height):
    root = ET.Element(f"{{{NS}}}svg", {"width": "1100", "height": str(height), "viewBox": f"0 0 1100 {height}",
                      "role": "img", "aria-label": title, "font-family": "Arial, Helvetica, sans-serif"})
    element(root, "title", content=title)
    element(root, "rect", {"width": 1100, "height": height, "fill": "white"})
    label(root, 30, 38, title, 24, font_weight="bold")
    label(root, 30, 65, subtitle, 14, "#526378")
    return root


def pair_label(pair):
    a, b = pair.split("-")
    return f"{C.NAMES[a]} / {C.NAMES[b]}"


def zero_chart(rows, path):
    svg = canvas("Figure 1. Correlation depends on the zero-category policy",
                 "Same records, taxonomy and Spearman estimator; only the treatment of shared zeros changes.", 690)
    left, right, top, step = 405, 890, 156, 46
    sx = lambda value: left+(value+1)*(right-left)/2
    element(svg, "circle", {"cx": 40, "cy": 98, "r": 5, "fill": BLUE})
    label(svg, 54, 103, "All taxonomy categories", 13)
    element(svg, "circle", {"cx": 285, "cy": 98, "r": 5, "fill": ORANGE})
    label(svg, 299, 103, "Drop shared zeros (inferred rule)", 13)
    label(svg, 950, 128, "All", 13, BLUE, "middle")
    label(svg, 1025, 128, "Drop", 13, ORANGE, "middle")
    for tick in (-1, -.5, 0, .5, 1):
        x = sx(tick)
        element(svg, "line", {"x1": x, "y1": top-20, "x2": x, "y2": top+step*8+23,
                             "stroke": "#91a1b4" if tick == 0 else "#e2e7ed"})
        label(svg, x, 570, f"{tick:g}", 13, anchor="middle")
    for index, row in enumerate(rows):
        y = top+index*step
        if row["strength_changed"] == "True":
            element(svg, "rect", {"x": 24, "y": y-20, "width": 1052, "height": 40, "fill": "#fff3e8"})
        label(svg, 30, y+5, f"{PANEL_NAMES[row['panel']]} | {pair_label(row['pair'])}", 13)
        a, b = float(row["all_rho"]), float(row["drop_rho"])
        element(svg, "line", {"x1": sx(a), "y1": y-4, "x2": sx(b), "y2": y+4, "stroke": "#76869a", "stroke_width": 2})
        for value, dy, color in ((a, -4, BLUE), (b, 4, ORANGE)):
            dot = element(svg, "circle", {"cx": sx(value), "cy": y+dy, "r": 5, "fill": color})
            element(dot, "title", content=f"{pair_label(row['pair'])}: rho={value:.6f}")
        label(svg, 950, y+5, f"{a:.3f}", 14, BLUE, "middle")
        label(svg, 1025, y+5, f"{b:.3f}", 14, ORANGE, "middle")
    label(svg, (left+right)/2, 597, "Spearman rank correlation (rho)", 14, anchor="middle")
    largest = max(rows, key=lambda r: abs(float(r["drop_rho"])-float(r["all_rho"])))
    label(svg, 30, 629, f"Largest rho change: {float(largest['all_rho']):.3f} to {float(largest['drop_rho']):.3f} "
          f"({largest['all_categories']} categories to {largest['nonsharedzero_categories']}).", 14)
    label(svg, 30, 654, "Highlight marks a strength-label change. Numerical agreement does not establish the authors' rule.", 13, "#526378")
    C.text(path, ET.tostring(svg, encoding="unicode")+"\n")


def bin_chart(rows, path, overview):
    selected = [r for r in rows if r["bucket_index"] == "0"]
    svg = canvas("Figure 2. First-bin shares change with endpoint conventions",
                 "One factor changed: half-open bins versus bins including their right endpoints. Denominator: 500 per OS.", 760)
    left, right, top, step = 315, 925, 160, 54
    sx = lambda value: left+value*(right-left)/100
    element(svg, "rect", {"x": 30, "y": 88, "width": 16, "height": 10, "fill": BLUE})
    label(svg, 54, 98, "Half-open: [0,10) or [0,3)", 13)
    element(svg, "rect", {"x": 350, "y": 88, "width": 16, "height": 10, "fill": ORANGE})
    label(svg, 374, 98, "Right-closed: [0,10] or [0,3]", 13)
    label(svg, 1025, 128, "Change (pp)", 13, anchor="middle")
    for tick in range(0, 101, 20):
        element(svg, "line", {"x1": sx(tick), "y1": 130, "x2": sx(tick), "y2": 620, "stroke": "#e2e7ed"})
        label(svg, sx(tick), 644, str(tick), 13, anchor="middle")
    pretty = {"lines": "Changed lines", "functions": "Involved functions", "files": "Modified files"}
    for index, row in enumerate(selected):
        y = top+index*step
        label(svg, 30, y+5, f"{pretty[row['metric']]} | {C.NAMES[row['os']]}", 14)
        for offset, key, color in ((-15, "half_open_pct", BLUE), (2, "right_closed_pct", ORANGE)):
            value = float(row[key])
            bar = element(svg, "rect", {"x": left, "y": y+offset, "width": sx(value)-left, "height": 12, "fill": color})
            element(bar, "title", content=f"{row['os']} {row['metric']} {key}: {value:.2f}%")
            label(svg, sx(value)+6, y+offset+11, f"{value:.1f}%", 12, color)
        label(svg, 1025, y+5, f"{float(row['delta_pp']):+.1f}", 14, anchor="middle")
    label(svg, (left+right)/2, 672, "Share of records in the first bin (%)", 14, anchor="middle")
    stable_first = sum(r["half_open_top_buckets"] == [0] and r["right_closed_guaranteed_unique_top"] == [0] for r in overview)
    label(svg, 30, 708, f"The first bin is the unique largest under both policies in {stable_first}/{len(overview)} OS/metric combinations.", 14)
    label(svg, 30, 734, f"Full results: {len(rows)} cells; assignments are listed in bucket_membership.csv. This is not a data correction.", 13, "#526378")
    C.text(path, ET.tostring(svg, encoding="unicode")+"\n")


def reports(out, zero, bins):
    summary = json.loads((out/"run_summary.json").read_text(encoding="utf-8"))
    stats = C.read_csv(out/"run_statistics.csv")
    runs = {int(r["runs"]) for r in stats}
    if len(runs) != 1 or min(runs) < 3:
        raise ValueError("report requires a consistent run count of at least three")
    n = min(runs)
    stat_map = {r["metric_id"]: r for r in stats}
    run_maps = [{r["metric_id"]: r["value"] for r in C.read_csv(out/f"runs/run{i}_metrics.csv")}
                for i in range(1, n+1)]
    comparisons = []

    def compare(key, paper, setting):
        stat = stat_map[key]
        mean = float(stat["mean"])
        gap = mean-float(paper)
        row = {"metric_id": key, "setting": setting, "unit": stat["unit"], "paper": paper}
        row.update({f"run{i}": values[key] for i, values in enumerate(run_maps, 1)})
        row.update({"mean": stat["mean"], "sample_sd": stat["sample_sd"], "signed_gap": f"{gap:.15g}",
                    "absolute_gap": f"{abs(gap):.15g}",
                    "relative_gap": "NA" if float(paper) == 0 else f"{abs(gap)/abs(float(paper)):.15g}",
                    "matches_printed": f"{mean:.2f}" == f"{float(paper):.2f}",
                    "verdict_scope": "printed-number agreement under this explicit candidate setting; not proof of author method"})
        comparisons.append(row)

    for r in zero:
        for policy in ("all_categories", "drop_shared_zeros"):
            compare(f"rho/{r['panel']}/{r['pair']}/{policy}", r["paper_rho"], policy)
    for r in bins:
        compare(f"pct/{r['metric']}/{r['os']}/{r['bucket_index']}/half_open", r["paper_pct"], "half_open_inferred")
    C.write_csv(out/"paper_vs_ours.csv", list(comparisons[0]), comparisons)

    def display(key, digits):
        row = stat_map[key]
        return f"{float(row['mean']):.{digits}f} ± {float(row['sample_sd']):.{digits}f}"

    issues = C.read_csv(out/"data_audit.csv")
    severity = summary["audit"]["severity_counts"]
    mismatch = [r for r in issues if r["code"] == "LINE_SUM_MISMATCH"]
    selected = [r for r in bins if r["bucket_index"] == "0"]
    changed = [r for r in zero if r["strength_changed"] == "True"]
    largest_rho = max(zero, key=lambda r: abs(float(r["drop_rho"])-float(r["all_rho"])))
    rho_note = (f"The largest rho change is {PANEL_NAMES[largest_rho['panel']]} for {pair_label(largest_rho['pair'])}: "
                f"{float(largest_rho['all_rho']):.6f} ({largest_rho['all_strength']}) to "
                f"{float(largest_rho['drop_rho']):.6f} ({largest_rho['drop_strength']}), using "
                f"{largest_rho['all_categories']} versus {largest_rho['nonsharedzero_categories']} categories. "
                "This establishes policy sensitivity, not the authors' actual unpublished preprocessing rule.")
    largest_bin = max(bins, key=lambda r: max(abs(float(r["delta_pp_min"])), abs(float(r["delta_pp_max"]))))
    largest_bin_note = f"{C.NAMES[largest_bin['os']]} {largest_bin['metric']}, bucket {largest_bin['bucket_index']} (zero-based)"
    uncertain = [r for r in bins if r["right_closed_count_min"] != r["right_closed_count_max"]]
    bound_note = ("Alternative-policy ambiguous cells: " + "; ".join(
        f"{C.NAMES[r['os']]} {r['metric']} {r['right_closed_interval']}: "
        f"[{float(r['right_closed_pct_min']):g}%,{float(r['right_closed_pct_max']):g}%]" for r in uncertain) + ". "
        if uncertain else "All alternative-policy cell shares are exactly identified. ")
    bound_note += ("These are identification bounds, not confidence intervals; their extremes are linked by "
                   "conservation and cannot be selected independently. All first-bin shares in the figure are exactly identified.")
    all_sd_zero = all(float(r["sample_sd"]) == 0 for r in stats)
    sd_note = "All numeric metrics have SD=0." if all_sd_zero else "Some numeric metrics have nonzero SD; inspect run_statistics.csv."
    lines = ["# Preprocessing Sensitivity and Dataset Consistency", "",
             "Prepared for 1240009531 吴彦阳 (Wu Yanyang), CS340 group replication.", "",
             "## Question and scope", "",
             "Do unspecified preprocessing conventions affect the reproduced numbers and interpretations when the published defect records stay fixed?",
             "This contribution complements the existing baseline, sample-size, severity, metric and bootstrap experiments. It does not re-collect defects or validate all author-provided labels.", "",
             "## Setup and controlled contrasts", "",
             f"Starting group commit: `{C.BASELINE_COMMIT}`. Inputs are the existing 1,500 labelled records and the group's transcribed Figures 2-4 references; SHA-256 hashes and actual environment are recorded in `logs/run1.json`.",
             "The implementation is standard-library Python and imports no teammate analysis module. Taxonomy order and reference schemas are attributed to the baseline.", "",
             "Experiment A changes only whether categories zero in both OS profiles are retained. It computes nine Figure 4(a-c) coefficients with average ranks for ties. Severity and repaired code elements are not silently added to the vectors. Figure 4(d) is excluded because its construction remains unspecified.", "",
             "Experiment B changes only bin endpoint inclusion: [0,c1), [c1,c2), ... versus [0,c1], (c1,c2], ... . The last bin is explicitly unbounded. The source figure's finite tail labels are stored separately and are not treated as known finite upper bounds for censored counts.",
             "Records, denominators, labels and metrics remain fixed. Zero-valued counts are retained; they are not silently interpreted as missing. A lower-bound value such as 20+ is assigned exactly only when every possible value is in the same bin. Ambiguous baseline membership blocks the analysis; ambiguous alternative membership is propagated as per-cell lower and upper bounds, not imputed.", "",
             "## Results: zero-category policy", "",
             "| Dimension | OS pair | Paper | All categories (mean ± SD) | Drop shared zeros (mean ± SD) | Categories all/drop |",
             "|---|---|---:|---:|---:|---:|"]
    for r in zero:
        prefix = f"rho/{r['panel']}/{r['pair']}/"
        lines.append(f"| {PANEL_NAMES[r['panel']]} | {pair_label(r['pair'])} | {r['paper_rho']} | {display(prefix+'all_categories', 3)} | {display(prefix+'drop_shared_zeros', 3)} | {r['all_categories']}/{r['nonsharedzero_categories']} |")
    lines += ["", f"All-category estimates match {summary['all_category_matches']}/9 printed coefficients after rounding; the inferred filter matches {summary['drop_shared_zero_matches']}/9. {len(changed)} of nine coefficients changes the paper's absolute-rho strength category.",
              rho_note, "",
              "![Zero-category comparison](figures/zero_policy.svg)", "", "## Results: bin endpoints", "",
              "| Metric | OS | Half-open first-bin % (mean ± SD) | Right-closed first-bin % (mean ± SD) | Delta (pp) |",
              "|---|---|---:|---:|---:|"]
    for r in selected:
        prefix = f"pct/{r['metric']}/{r['os']}/0/"
        lines.append(f"| {r['metric']} | {C.NAMES[r['os']]} | {display(prefix+'half_open', 2)} | {display(prefix+'right_closed_min', 2)} | {float(r['delta_pp']):+.2f} |")
    stable = sum(r["top_set_unchanged"] for r in summary["histogram_overview"])
    lines += ["", f"The half-open reconstruction matches {summary['half_open_histogram_matches']}/39 printed histogram cells. The largest cell change is {summary['largest_absolute_bucket_change_pp']:.2f} percentage points ({largest_bin_note}). The set of modal bins is unchanged in {stable}/9 OS/metric combinations.",
              bound_note,
              "Thus, exact percentages are endpoint-sensitive, while the narrower descriptive statement that the first bin is most frequent survives these two policies. Most frequent does not necessarily mean a majority. Repairs above 500 changed lines were filtered by the paper, so this does not establish the distribution of all OS repairs.", "",
              "![Endpoint comparison](figures/binning_policy.svg)", "", "## Dataset audit", "",
              f"The audit found {severity['ERROR']} blocking errors, {severity['WARN']} warning(s), and {severity['INFO']} informational flags. Warning/info flags do not imply that labels are incorrect."]
    for r in mismatch:
        lines.append(f"- {r['os']} defect {r['bug_ids']}: total changed lines is {r['observed']}; {r['expected_or_context']}. An aggregate histogram match does not establish record-level arithmetic consistency.")
    lines += ["", "Zero involved-function values and shared full Patch fields are reported as context, not automatically repaired or deduplicated. A shared field is not proof of duplicate defects. The audit did not download or relabel all source patches.", "",
              "## Repeated runs and traceability", "",
              f"{n} separate Python processes generated 135 scalar metrics/bounds per run (18 correlations, 39 baseline percentages and 78 alternative lower/upper percentages). `runs/runN_metrics.csv` contains the actual values; `run_statistics.csv` contains their means and sample standard deviations. {sd_note} This measures execution repeatability only, not sampling error, annotation error or population uncertainty.",
              "`paper_vs_ours.csv` contains 57 comparisons with paper values, every actual run, mean, sample SD, signed/absolute/relative gaps, and the candidate preprocessing setting. Alternative endpoint bounds remain in `binning_comparison.csv` because they refer to different intervals, rather than an identical-setting error test. Repeat-run SDs are not uncertainty intervals.",
              "`determinism.json` compares every scientific output hash across runs, excluding environment/time metadata. `bucket_membership.csv` traces all 4,500 metric assignments to OS and Bug ID; `boundary_records.csv` isolates moved or ambiguously assigned records; `correlation_vectors.csv` preserves the exact category-count inputs.",
              "Percentage gaps are in percentage points. Rho gaps are absolute coefficient differences. Relative gaps use abs(ours-paper)/abs(paper), stored as ratios; zero paper values use NA, and near-zero rho makes relative gaps unstable. The alternative endpoint policy changes the interval definition, so its difference is a sensitivity contrast, not an error against an identical setting.", "",
              "## Verdicts and limits", "",
              "| Group claim addressed | Verdict within this module | Evidence and boundary |",
              "|---|---|---|",
              f"| C2: selected repairs concentrate in smaller bins (Figures 2-3) | Partially supported | {summary['half_open_histogram_matches']}/39 printed shares agree under an inferred convention; {stable}/9 modal-bin sets are stable. Precise percentages and zero/censored-value interpretation depend on definitions. |",
              f"| C3: similarity depends on dimension (Figure 4) | Partially supported | {summary['drop_shared_zero_matches']}/9 marginal values agree under an inferred filter; strength-label changes: {len(changed)}. Overall panel d is excluded and remains unresolved. |",
              "| C1: defect composition (Table II) | Not evaluated here | Reuse the attributed group's baseline evidence; this audit does not supply a new label-validity test. |", "",
              f"- Numeric aggregation: {summary['half_open_histogram_matches']}/39 histogram cells agree under the group's inferred half-open convention; {summary['drop_shared_zero_matches']}/9 marginal correlations agree under its inferred zero filter.",
              f"- Robustness: correlation strength-label changes under zero handling: {len(changed)}; stable modal-bin sets: {stable}/9.",
              "- Overall paper conclusions: only partially addressed. Neither numerical agreement nor these sensitivity checks independently validates the labels, selection process, causal maturity explanations or all-system generalization.",
              "- Fixed descriptive taxonomy: each rho is over only 6-8 categories. No new significance test or population confidence claim is made.", "",
              "## Attribution, contribution and AI usage", "",
              "Existing labelled data, paper transcriptions and taxonomy conventions come from the group baseline, credited in ../docs/METHODS.md and ../docs/MEMBER_CONTRIBUTION.md. This module adds its own audit, controlled contrasts, record-level evidence, repeated-run summaries and charts. Existing teammates' experiments remain attributed to them.",
              "AI assistance was used for planning, implementation, tests and drafting. The named student must inspect and understand the contribution before submission; this report does not claim that such review or manual relabelling has already occurred.", "",
              "## References", "",
              "1. H. Zuo, J. Li, J. Jiang. Toward Understanding Operating System Defects. arXiv:2608.20643v1, 2026. https://arxiv.org/html/2608.20643v1 (III-A, III-C, IV-A5 and IV-C).",
              "2. Author-released dashboard: https://zuohongyao.github.io/ . The baseline source manifest pins the snapshot.",
              f"3. CS340 group baseline: https://github.com/Lx-1-2-3-4/cs340-os-defects-replication/tree/{C.BASELINE_COMMIT} .",
              "4. CS340 Research Paper Replication, Academic Year 2026-2027, supplied course instructions. This is a member analysis supplement, not the complete group Final Report.", ""]
    C.text(out/"REPORT.md", "\n".join(lines))
    # Self-contained, offline HTML preview, including the actual SVG chart data.
    blocks = []
    in_table = False
    for line in lines:
        if line.startswith("!["):
            name = "zero_policy.svg" if "zero_policy" in line else "binning_policy.svg"
            blocks.append((out/"figures"/name).read_text(encoding="utf-8"))
        elif line.startswith("|"):
            if set(line.replace("|", "").replace(":", "").replace("-", "").strip()) == set():
                continue
            if not in_table:
                blocks.append("<table>");in_table = True
            blocks.append("<tr>"+"".join("<td>"+html.escape(s.strip())+"</td>" for s in line.strip("|").split("|"))+"</tr>")
        else:
            if in_table:
                blocks.append("</table>");in_table = False
            if line.startswith("# "):
                blocks.append("<h1>"+html.escape(line[2:])+"</h1>")
            elif line.startswith("## "):
                blocks.append("<h2>"+html.escape(line[3:])+"</h2>")
            elif line:
                blocks.append("<p>"+html.escape(line)+"</p>")
    if in_table:
        blocks.append("</table>")
    C.text(out/"REPORT.html", '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Preprocessing Sensitivity - 1240009531</title><style>body{font:16px/1.6 Arial,sans-serif;color:#18283b;max-width:1120px;margin:36px auto;padding:0 24px}h1{line-height:1.2}h2{margin-top:36px}table{border-collapse:collapse;width:100%;font-size:14px}td{border-bottom:1px solid #dce3eb;padding:8px;text-align:left}tr:first-child{font-weight:bold;background:#eef3f8}svg{width:100%;height:auto;margin:20px 0}p{max-width:100ch}@media print{body{margin:0}svg,table{break-inside:avoid}}</style><body>'+"\n".join(blocks)+"</body></html>\n")


def generate(out):
    C.invalidate_completion(out)
    zero = C.read_csv(out/"zero_policy_comparison.csv")
    bins = C.read_csv(out/"binning_comparison.csv")
    zero_chart(zero, out/"figures/zero_policy.svg")
    summary = json.loads((out/"run_summary.json").read_text(encoding="utf-8"))
    bin_chart(bins, out/"figures/binning_policy.svg", summary["histogram_overview"])
    reports(out, zero, bins)
    print("generated two native SVG charts and English Markdown/HTML report")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=C.ROOT/"results")
    generate(parser.parse_args().out_dir)
