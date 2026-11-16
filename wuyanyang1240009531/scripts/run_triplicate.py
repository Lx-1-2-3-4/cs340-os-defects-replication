"""Execute at least three actual runs, preserve numeric evidence and hash checks."""
from __future__ import annotations
import datetime
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path
import core as C


def prepare_output(out):
    """Invalidate stale aggregate artifacts and remove only owned run filenames."""
    C.invalidate_completion(out)
    for name in ("determinism.json", "run_statistics.csv", "paper_vs_ours.csv", "REPORT.md", "REPORT.html",
                 "figures/zero_policy.svg", "figures/binning_policy.svg"):
        (out/name).unlink(missing_ok=True)
    for folder, pattern in (("runs", r"run[1-9]\d*_metrics\.csv"), ("logs", r"run[1-9]\d*\.(json|log)")):
        if (out/folder).is_dir():
            for path in (out/folder).iterdir():
                if path.is_file() and re.fullmatch(pattern, path.name):
                    path.unlink()


def run(args):
    if isinstance(args.runs, bool) or not isinstance(args.runs, int) or args.runs < 3:
        raise ValueError("at least three runs are required")
    out = args.out_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    prepare_output(out)
    all_metrics, hashes = [], []
    for index in range(1, args.runs+1):
        with C.ScratchDirectory(parent=out.parent) as folder:
            temporary = Path(folder)
            command = [sys.executable, "-B", str(C.ROOT/"scripts/run_sensitivity.py"), "--data-dir", str(args.data_dir.resolve()),
                       "--paper-dir", str(args.paper_dir.resolve()), "--out-dir", str(temporary)]
            started = datetime.datetime.now(datetime.timezone.utc).isoformat()
            tick = time.perf_counter()
            proc = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace",
                                  env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"})
            C.text(out/f"logs/run{index}.log", proc.stdout + "\nSTDERR:\n" + proc.stderr)
            if proc.returncode:
                raise RuntimeError(f"run {index} failed with status {proc.returncode}; inspect logs/run{index}.log")
            numeric_files = {p.name: C.sha(p) for p in sorted(temporary.iterdir()) if p.is_file() and p.name != "run_metadata.json"}
            hashes.append(numeric_files)
            loaded = C.read_csv(temporary/"run_metrics.csv")
            metrics = {r["metric_id"]: (r["unit"], float(r["value"])) for r in loaded}
            if len(metrics) != len(loaded):
                raise ValueError("duplicate metric IDs")
            all_metrics.append(metrics)
            (out/"runs").mkdir(exist_ok=True)
            shutil.copy2(temporary/"run_metrics.csv", out/f"runs/run{index}_metrics.csv")
            meta = json.loads((temporary/"run_metadata.json").read_text(encoding="utf-8"))
            meta.update({"run": index, "started_utc": started, "elapsed_seconds": round(time.perf_counter()-tick, 6),
                         "returncode": proc.returncode, "command": "python -B scripts/run_sensitivity.py --data-dir <recorded-input> --paper-dir <recorded-reference> --out-dir <isolated-run>",
                         "scientific_output_sha256": numeric_files,
                         "execution_log_sha256": C.sha(out/f"logs/run{index}.log")})
            C.write_json(out/f"logs/run{index}.json", meta)
            if index == 1:
                for path in temporary.iterdir():
                    if path.is_file() and path.name != "run_metadata.json":
                        shutil.copy2(path, out/path.name)
            print(f"completed independent process {index}/{args.runs}", flush=True)
    if any(set(m) != set(all_metrics[0]) for m in all_metrics):
        raise ValueError("metric sets differ between runs")
    identical = all(h == hashes[0] for h in hashes)
    stats = []
    for key, (unit, _) in all_metrics[0].items():
        values = [m[key][1] for m in all_metrics]
        stats.append({"metric_id": key, "unit": unit, "runs": args.runs,
                      "mean": f"{statistics.mean(values):.15g}", "sample_sd": f"{statistics.stdev(values):.15g}",
                      "minimum": f"{min(values):.15g}", "maximum": f"{max(values):.15g}"})
    C.write_csv(out/"run_statistics.csv", list(stats[0]), stats)
    C.write_json(out/"determinism.json", {"runs": args.runs, "all_scientific_outputs_identical": identical,
                 "per_run_sha256": hashes, "interpretation": "SD measures repeat execution only, not sampling or label uncertainty."})
    if not identical:
        raise RuntimeError("scientific outputs differ between runs; no zero-SD assumption is allowed")
    print(f"verified {args.runs} identical runs; {len(stats)} actual means and sample SDs")


if __name__ == "__main__":
    run(C.arguments(__doc__, runs=True))
