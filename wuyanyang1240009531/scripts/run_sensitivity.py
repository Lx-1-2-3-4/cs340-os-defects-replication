"""Run the audited, one-factor-at-a-time preprocessing comparisons offline."""
from __future__ import annotations
import json
import os
import platform
import subprocess
import sys
from collections import Counter
from pathlib import Path
import core as C
import audit_data


def unique_reference(path, keys, value):
    result = {}
    for row in C.read_csv(path):
        key = tuple(row[k] for k in keys)
        if key in result:
            raise ValueError(f"duplicate paper-reference key {key}")
        result[key] = float(row[value])
    return result


def zero_experiment(records, paper_dir):
    paper = unique_reference(paper_dir/"fig4.csv", ("panel", "pair"), "paper_rho")
    rows, vectors, metrics = [], [], []
    for panel, (field, categories) in C.PANELS.items():
        counts = {tag: Counter(r[field] for r in records[tag]) for tag in C.SYSTEMS}
        for left, right in C.PAIRS:
            pair = f"{left}-{right}"
            x = [counts[left][cat] for cat in categories]
            y = [counts[right][cat] for cat in categories]
            keep = [i for i, (a, b) in enumerate(zip(x, y)) if a or b]
            all_rho = C.spearman(x, y)
            drop_rho = C.spearman([x[i] for i in keep], [y[i] for i in keep])
            target = paper[(panel, pair)]
            row = {
                "panel": panel, "pair": pair, "paper_rho": f"{target:.2f}",
                "all_categories": len(categories), "nonsharedzero_categories": len(keep),
                "all_rho": f"{all_rho:.15g}", "drop_rho": f"{drop_rho:.15g}",
                "drop_minus_all": f"{drop_rho-all_rho:.15g}",
                "all_abs_gap": f"{abs(all_rho-target):.15g}", "drop_abs_gap": f"{abs(drop_rho-target):.15g}",
                "all_relative_gap": "NA" if target == 0 else f"{abs(all_rho-target)/abs(target):.15g}",
                "drop_relative_gap": "NA" if target == 0 else f"{abs(drop_rho-target)/abs(target):.15g}",
                "all_matches_printed": f"{all_rho:.2f}" == f"{target:.2f}",
                "drop_matches_printed": f"{drop_rho:.2f}" == f"{target:.2f}",
                "all_strength": C.strength(all_rho), "drop_strength": C.strength(drop_rho),
                "strength_changed": C.strength(all_rho) != C.strength(drop_rho),
            }
            rows.append(row)
            for category, a, b in zip(categories, x, y):
                vectors.append({"panel": panel, "pair": pair, "category": category,
                                "left_count": a, "right_count": b, "shared_zero": a == b == 0})
            for policy, value in (("all_categories", all_rho), ("drop_shared_zeros", drop_rho)):
                metrics.append({"metric_id": f"rho/{panel}/{pair}/{policy}", "unit": "rho", "value": f"{value:.15g}"})
    return rows, vectors, metrics


def bin_experiment(records, paper_dir):
    fig2 = unique_reference(paper_dir/"fig2.csv", ("os", "bucket"), "paper_pct")
    fig3 = unique_reference(paper_dir/"fig3.csv", ("os", "metric", "bucket"), "paper_pct")
    rows, membership, metrics, overview = [], [], [], []
    for metric, (field, cuts, paper_labels) in C.METRICS.items():
        for tag in C.SYSTEMS:
            rs = records[tag]
            counts = {policy: Counter() for policy in ("half_open", "right_min", "right_max")}
            for record in rs:
                a = C.bucket(record[field], cuts, "half_open")
                possible = C.possible_buckets(record[field], cuts, "right_closed")
                b = possible[0] if len(possible) == 1 else None
                counts["half_open"][a] += 1
                for index in possible:
                    counts["right_max"][index] += 1
                if b is not None:
                    counts["right_min"][b] += 1
                membership.append({
                    "os": tag, "bug_id": record["Bug ID"], "metric": metric,
                    "source_value": record[field], "censored": C.parse_count(record[field]).censored,
                    "half_open_bucket": a, "right_closed_bucket": "" if b is None else b,
                    "right_closed_possible_buckets": "|".join(str(i) for i in possible),
                    "movement": "possible" if b is None and a in possible else "moved" if a not in possible else "unchanged",
                })
            if sum(counts["half_open"].values()) != len(rs) or not sum(counts["right_min"].values()) <= len(rs) <= sum(counts["right_max"].values()):
                raise AssertionError("histogram bounds do not conserve records")
            top_a = [i for i in range(len(paper_labels)) if counts["half_open"][i] == max(counts["half_open"].values())]
            guaranteed = [i for i in range(len(paper_labels)) if all(counts["right_min"][i] > counts["right_max"][j] for j in range(len(paper_labels)) if j != i)]
            overview.append({"os": tag, "metric": metric, "half_open_top_buckets": top_a, "right_closed_guaranteed_unique_top": guaranteed,
                             "top_set_unchanged": len(top_a) == 1 and top_a == guaranteed,
                             "uncertain_alternative_records": sum(len(C.possible_buckets(r[field], cuts, "right_closed")) > 1 for r in rs)})
            for i, label in enumerate(paper_labels):
                a, low, high = counts["half_open"][i], counts["right_min"][i], counts["right_max"][i]
                ap, lp, hp = 100*a/len(rs), 100*low/len(rs), 100*high/len(rs)
                target = fig2[(tag, label)] if metric == "lines" else fig3[(tag, metric, label)]
                rows.append({
                    "os": tag, "metric": metric, "bucket_index": i, "paper_bucket_label": label,
                    "half_open_interval": C.interval(cuts, i, "half_open"),
                    "right_closed_interval": C.interval(cuts, i, "right_closed"),
                    "denominator": len(rs), "half_open_count": a, "right_closed_count": low if low == high else "",
                    "right_closed_count_min": low, "right_closed_count_max": high,
                    "half_open_pct": f"{ap:.8f}", "right_closed_pct": f"{lp:.8f}" if low == high else "",
                    "right_closed_pct_min": f"{lp:.8f}", "right_closed_pct_max": f"{hp:.8f}",
                    "delta_pp": f"{lp-ap:.8f}" if low == high else "", "delta_pp_min": f"{lp-ap:.8f}", "delta_pp_max": f"{hp-ap:.8f}",
                    "paper_pct": f"{target:.2f}", "half_open_abs_gap_pp": f"{abs(ap-target):.8f}",
                    "half_open_relative_gap": "NA" if target == 0 else f"{abs(ap-target)/abs(target):.12g}",
                    "half_open_matches_printed": f"{ap:.2f}" == f"{target:.2f}",
                })
                for policy, value in (("half_open", ap), ("right_closed_min", lp), ("right_closed_max", hp)):
                    metrics.append({"metric_id": f"pct/{metric}/{tag}/{i}/{policy}", "unit": "percentage_points", "value": f"{value:.15g}"})
    return rows, membership, metrics, overview


def environment():
    """Portable metadata; no username-dependent absolute paths are emitted."""
    memory = None
    try:
        if os.name == "nt":
            import ctypes
            class Memory(ctypes.Structure):
                _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [(name, ctypes.c_ulonglong) for name in
                    ("total_physical", "available_physical", "total_page", "available_page", "total_virtual", "available_virtual", "extended")]
            status = Memory()
            status.length = ctypes.sizeof(Memory)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                memory = status.total_physical
        elif hasattr(os, "sysconf"):
            memory = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    except (AttributeError, OSError, ValueError):
        pass
    return {"python": platform.python_version(), "implementation": platform.python_implementation(),
            "os": platform.system(), "os_release": platform.release(), "kernel_or_build": platform.version(),
            "machine": platform.machine(), "processor": platform.processor() or "not reported by platform",
            "logical_cpus": os.cpu_count(), "physical_memory_bytes": memory,
            "compiler": "not used: interpreted Python and standard library only"}


def metadata(data_dir, paper_dir):
    def git(*args):
        try:
            top = subprocess.check_output(["git", "-C", str(C.GROUP), "rev-parse", "--show-toplevel"],
                                          text=True, stderr=subprocess.DEVNULL).strip()
            if Path(top).resolve() != C.GROUP.resolve():
                return None  # A source export must not inherit an ancestor repository's revision.
            return subprocess.check_output(["git", "-C", str(C.GROUP), *args], text=True, stderr=subprocess.DEVNULL).strip()
        except (OSError, subprocess.CalledProcessError):
            return None
    inputs = {f"data/{p.name}": C.sha(p) for p in sorted(Path(data_dir).glob("defects_*.json"))}
    inputs["data/PROVENANCE.json"] = C.sha(Path(data_dir)/"PROVENANCE.json")
    inputs.update({f"paper/{name}": C.sha(Path(paper_dir)/name) for name in ("fig2.csv", "fig3.csv", "fig4.csv")})
    sources = {str(p.relative_to(C.ROOT)).replace("\\", "/"): C.sha(p) for folder in ("scripts", "tests")
               for p in sorted((C.ROOT/folder).glob("*.py"))}
    dirty = git("status", "--porcelain", "--untracked-files=normal")
    return {"member": "1240009531 吴彦阳", "baseline_commit": C.BASELINE_COMMIT,
            "checkout_commit": git("rev-parse", "HEAD"), "working_tree_dirty": None if dirty is None else bool(dirty),
            "input_sha256": inputs, "source_sha256": sources, "environment": environment(),
            "design": "Two separate single-factor experiments; no relabelling, no data repair, no stochastic resampling.",
            "tail_intervals": "Unbounded final bins; finite labels in the paper are retained only as source labels."}


def run(args):
    records = C.load(args.data_dir)
    audit = audit_data.save(records, args.data_dir, args.out_dir)
    if audit["severity_counts"]["ERROR"]:
        raise ValueError("blocking audit error(s); see data_audit.csv; no analysis performed")
    zero, vectors, metric_a = zero_experiment(records, args.paper_dir)
    bins, membership, metric_b, overview = bin_experiment(records, args.paper_dir)
    if len(zero) != 9 or len(bins) != 39 or len(metric_a+metric_b) != 135:
        raise AssertionError("incomplete experiment coverage")
    out = args.out_dir
    for name, values in (("zero_policy_comparison", zero), ("correlation_vectors", vectors),
                         ("binning_comparison", bins), ("bucket_membership", membership),
                         ("boundary_records", [r for r in membership if r["movement"] != "unchanged"]),
                         ("run_metrics", metric_a+metric_b)):
        # An otherwise valid input can have no boundary movements.
        fields = list(values[0]) if values else list(membership[0])
        C.write_csv(out/f"{name}.csv", fields, values)
    max_gap = lambda row: max(abs(float(row["delta_pp_min"])), abs(float(row["delta_pp_max"])))
    maximum = max(bins, key=max_gap)
    summary = {"records": 1500, "zero_comparisons": len(zero), "histogram_cells": len(bins), "metrics": 135,
               "all_category_matches": sum(r["all_matches_printed"] for r in zero),
               "drop_shared_zero_matches": sum(r["drop_matches_printed"] for r in zero),
               "rho_strength_changes": sum(r["strength_changed"] for r in zero),
               "half_open_histogram_matches": sum(r["half_open_matches_printed"] for r in bins),
               "largest_absolute_bucket_change_pp": max_gap(maximum),
               "uncertain_alternative_cells": sum(r["right_closed_count_min"] != r["right_closed_count_max"] for r in bins),
               "largest_change_cell": {key: maximum[key] for key in ("os", "metric", "bucket_index")},
               "histogram_overview": overview, "audit": audit,
               "interpretation": "Rounding agreement is distinct from methodological validation; a sensitivity contrast is not a correction."}
    C.write_json(out/"run_summary.json", summary)
    C.write_json(out/"run_metadata.json", metadata(args.data_dir, args.paper_dir))
    print(f"audit: {audit['severity_counts']}; baseline histogram matches: {summary['half_open_histogram_matches']}/39")
    print(f"rho matches: full categories {summary['all_category_matches']}/9; inferred zero filter {summary['drop_shared_zero_matches']}/9")
    print(f"largest bucket change: {summary['largest_absolute_bucket_change_pp']:.2f} pp; 135 metrics/bounds recorded")
    return summary


if __name__ == "__main__":
    run(C.arguments(__doc__))
