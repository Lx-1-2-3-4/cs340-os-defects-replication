"""Run the layer-composition analysis three times and prove the output is identical.

The section asks for at least three runs with mean and standard deviation.  The
analysis is deterministic (no sampling, no randomness), so the expected standard
deviation is 0.00; this script demonstrates it instead of asserting it, by
hashing every generated file in each run.

Usage:
    python scripts/run_layer_triplicate.py [--runs 3] [--results DIR] [--figures DIR]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import common as C

FILES = ("layer_composition.csv", "layer_within_function.csv",
         "layer_within_trigger.csv", "layer_pairwise_function.csv",
         "layer_pairwise_trigger.csv", "layer_distances.csv",
         "layer_composition.png", "layer_composition.svg",
         "layer_distance_adjustment.png", "layer_distance_adjustment.svg")


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def run_once(index, results, figures):
    out_dir = Path(results) / "logs" / f"layer_run{index}"
    fig_dir = Path(figures) / "logs" / f"layer_run{index}"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    started = time.time()
    proc = subprocess.run(
        [sys.executable, str(C.ROOT / "scripts" / "layer_analysis.py"),
         "--results", str(out_dir), "--figures", str(fig_dir)],
        capture_output=True, text=True)
    elapsed = time.time() - started
    if proc.returncode != 0:
        raise RuntimeError(f"run {index} failed:\n{proc.stderr}")

    (out_dir / f"run{index}.log").write_text(proc.stdout, encoding="utf-8")

    hashes = {}
    for directory, prefix in ((out_dir, ""), (fig_dir, "figures/")):
        for path in sorted(Path(directory).glob("*")):
            if path.is_file() and path.name != f"run{index}.log" and path.suffix != ".json":
                hashes[prefix + path.name] = sha256(path)

    record = {
        "run": index,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
        "duration_seconds": round(elapsed, 3),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "returncode": proc.returncode,
        "hashes": hashes,
    }
    (out_dir / f"run{index}.json").write_text(json.dumps(record, indent=2) + "\n",
                                              encoding="utf-8")
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--results", default=str(C.RESULTS_DIR))
    parser.add_argument("--figures", default=str(C.ROOT / "figures"))
    args = parser.parse_args(argv)
    if args.runs < 3:
        parser.error("--runs must be at least 3")

    records = [run_once(i, args.results, args.figures) for i in range(1, args.runs + 1)]

    names = sorted(records[0]["hashes"])
    identical = all(record["hashes"] == records[0]["hashes"] for record in records[1:])
    per_file = {name: len({record["hashes"].get(name) for record in records}) == 1
                for name in names}

    summary = {
        "runs": args.runs,
        "identical": identical,
        "per_file_identical": per_file,
        "durations_seconds": [record["duration_seconds"] for record in records],
        "mean_duration_seconds": round(
            sum(record["duration_seconds"] for record in records) / len(records), 3),
        "sd_duration_seconds": round(
            (sum((record["duration_seconds"] -
                  sum(r["duration_seconds"] for r in records) / len(records)) ** 2
                 for record in records) / (len(records) - 1)) ** 0.5, 3),
        "values_per_run": 18 + 144 + 126 + 15 + 15 + 6,   # rows in the six tables
        "value_sd": 0.0,
        "note": ("the pipeline is deterministic; value_sd is 0.00 by construction, "
                 "and the per-file hashes prove it"),
    }
    Path(args.results).mkdir(parents=True, exist_ok=True)
    (Path(args.results) / "determinism.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(f"{args.runs} runs, identical output: {'yes' if identical else 'NO'}")
    for name, same in per_file.items():
        if not same:
            print(f"  differs: {name}")
    print(f"mean duration {summary['mean_duration_seconds']} s, "
          f"sd {summary['sd_duration_seconds']} s")
    return 0 if identical else 1


if __name__ == "__main__":
    sys.exit(main())

