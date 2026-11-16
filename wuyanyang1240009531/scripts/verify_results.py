"""Verify every regenerated cell, raw run metric, statistic and chart, not totals alone."""
from __future__ import annotations
import argparse
import json
import math
import statistics
import datetime
import re
from pathlib import Path
from types import SimpleNamespace
import core as C
import run_sensitivity
import plot_results


def metric_map(path):
    rows = C.read_csv(path)
    result = {}
    for row in rows:
        key = row["metric_id"]
        if key in result or not math.isfinite(float(row["value"])):
            raise ValueError(f"duplicate or nonfinite metric: {key}")
        result[key] = (row["unit"], float(row["value"]))
    return result


def verify(out, data_dir, paper_dir):
    out = Path(out)
    C.invalidate_completion(out)
    problems = []
    with C.ScratchDirectory(parent=out.parent) as folder:
        expected = Path(folder)
        run_sensitivity.run(SimpleNamespace(data_dir=Path(data_dir), paper_dir=Path(paper_dir), out_dir=expected))
        scientific = {p.name: C.sha(p) for p in expected.iterdir() if p.is_file() and p.name != "run_metadata.json"}
        for name, digest in scientific.items():
            if not (out/name).is_file() or C.sha(out/name) != digest:
                problems.append(f"regenerated content mismatch: {name}")
        target = metric_map(expected/"run_metrics.csv")
        detail = json.loads((out/"determinism.json").read_text(encoding="utf-8"))
        n = detail["runs"]
        if not isinstance(n, int) or isinstance(n, bool) or n < 3:
            raise ValueError("at least three real runs must be recorded")
        if detail["all_scientific_outputs_identical"] is not True:
            problems.append("scientific output determinism failed")
        if len(detail["per_run_sha256"]) != n:
            problems.append("wrong number of hash manifests")
        for folder, pattern, wanted in (
            ("runs", r"run[1-9]\d*_metrics\.csv", {f"run{i}_metrics.csv" for i in range(1, n+1)}),
            ("logs", r"run[1-9]\d*\.(json|log)", {f"run{i}.{ext}" for i in range(1, n+1) for ext in ("json", "log")}),
        ):
            actual = {p.name for p in (out/folder).iterdir() if re.fullmatch(pattern, p.name)}
            if actual != wanted:
                problems.append(f"extra or missing run artifacts: {folder}")
        run_values = []
        expected_meta = run_sensitivity.metadata(Path(data_dir), Path(paper_dir))
        for index in range(1, n+1):
            m = metric_map(out/f"runs/run{index}_metrics.csv")
            run_values.append(m)
            if m != target:
                problems.append(f"numeric metric mismatch: run {index}")
            meta = json.loads((out/f"logs/run{index}.json").read_text(encoding="utf-8"))
            if meta["source_sha256"] != expected_meta["source_sha256"] or meta["input_sha256"] != expected_meta["input_sha256"]:
                problems.append(f"stale source/input manifest: run {index}")
            if meta["returncode"] != 0 or meta["run"] != index:
                problems.append(f"invalid successful-run evidence: run {index}")
            if meta["scientific_output_sha256"] != scientific or detail["per_run_sha256"][index-1] != scientific:
                problems.append(f"scientific hash mismatch: run {index}")
            if not (out/f"logs/run{index}.log").is_file():
                problems.append(f"missing execution log: run {index}")
            elif meta.get("execution_log_sha256") != C.sha(out/f"logs/run{index}.log"):
                problems.append(f"execution log hash mismatch: run {index}")
            elapsed = meta.get("elapsed_seconds")
            if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) or not math.isfinite(elapsed) or elapsed < 0:
                problems.append(f"invalid elapsed time: run {index}")
            try:
                started = datetime.datetime.fromisoformat(meta["started_utc"])
                if started.utcoffset() != datetime.timedelta(0):
                    raise ValueError("start timestamp must identify UTC")
            except (KeyError, TypeError, ValueError):
                problems.append(f"invalid UTC start time: run {index}")
        stat_rows = C.read_csv(out/"run_statistics.csv")
        stat_map = {r["metric_id"]: r for r in stat_rows}
        if len(stat_map) != len(stat_rows) or set(stat_map) != set(target):
            problems.append("statistics keys are incomplete or duplicated")
        else:
            for key, (unit, _) in target.items():
                values = [m[key][1] for m in run_values]
                row = stat_map[key]
                wants = {"mean": statistics.mean(values), "sample_sd": statistics.stdev(values),
                         "minimum": min(values), "maximum": max(values)}
                if row["unit"] != unit or int(row["runs"]) != n:
                    problems.append(f"statistics metadata mismatch: {key}")
                for field, value in wants.items():
                    if not math.isclose(float(row[field]), value, rel_tol=1e-12, abs_tol=1e-12):
                        problems.append(f"statistics value mismatch: {key}/{field}")
        if not problems:
            # Render from recomputed data and recorded run statistics to detect
            # stale charts/report text without trusting existing SVG labels.
            (expected/"run_statistics.csv").write_bytes((out/"run_statistics.csv").read_bytes())
            (expected/"runs").mkdir()
            for index in range(1, n+1):
                (expected/f"runs/run{index}_metrics.csv").write_bytes((out/f"runs/run{index}_metrics.csv").read_bytes())
            plot_results.generate(expected)
            for name in ("paper_vs_ours.csv", "figures/zero_policy.svg", "figures/binning_policy.svg", "REPORT.md", "REPORT.html"):
                if not (out/name).is_file() or C.sha(out/name) != C.sha(expected/name):
                    problems.append(f"stale presentation artifact: {name}")
    if problems:
        raise ValueError("\n".join(problems))
    return {"verified": True, "scientific_files": len(scientific), "metric_count": len(target),
            "runs": n, "charts": 2, "scope": "full cell regeneration, run-level evidence, statistics and chart/report rebuild"}


def main():
    args = C.arguments(__doc__)
    result = verify(args.out_dir, args.data_dir, args.paper_dir)
    C.write_json(args.out_dir/"verification.json", result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
