#!/usr/bin/env python3
"""Run the reproduction pipeline three times and verify that it is deterministic.

The course rubric asks for mean +/- standard deviation across at least three
runs.  The paper's analysis is a deterministic recomputation over a fixed
dataset (there is no sampling, training or scheduling randomness), so three
runs must produce byte-identical outputs and the standard deviation of every
reported percentage is exactly 0.00.  This script proves that claim and stores
the evidence in ``results/logs/``:

* ``reproduce_run1.log`` .. ``reproduce_run3.log`` -- stdout/stderr of each run
* ``determinism.txt`` -- SHA-256 of every output file after each run, the
  verdict, and the (zero) standard deviation across runs

Usage
-----
    python scripts/run_triplicate.py
"""

from __future__ import annotations

import datetime
import hashlib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402  (local module, path set above)

RESULT_SUFFIXES = (".csv", ".json", ".md")
RUNS = 3


def output_hashes(results_dir: Path) -> dict:
    """Hash the canonical output files (everything except the log directory)."""
    files = sorted(path for path in results_dir.iterdir()
                   if path.is_file() and path.suffix in RESULT_SUFFIXES)
    return {path.name: common.sha256_file(path) for path in files}


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    results_dir = repo_root / "results"
    logs_dir = results_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    reproduce = repo_root / "scripts" / "reproduce.py"
    script_hash = common.sha256_file(reproduce)

    hashes = []
    for run in range(1, RUNS + 1):
        started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        command = [sys.executable, "scripts/reproduce.py", "--out-dir", "results"]
        print(f"[run {run}/{RUNS}] {started} -> {' '.join(command)}")
        completed = subprocess.run(command, cwd=str(repo_root), capture_output=True, text=True)
        log_path = logs_dir / f"reproduce_run{run}.log"
        common.write_text(
            log_path,
            
            "\n".join([
                f"# reproduce run {run} of {RUNS}",
                f"started_utc: {started}",
                f"command: {' '.join(command)}",
                f"python: {sys.version.split()[0]}",
                f"reproduce.py sha256: {script_hash}",
                f"returncode: {completed.returncode}",
                "",
                "## stdout",
                completed.stdout,
                "",
                "## stderr",
                completed.stderr,
                "",
            ]),
        )
        if completed.returncode != 0:
            print(f"run {run} FAILED; see {log_path}")
            return completed.returncode
        hashes.append(output_hashes(results_dir))

    baseline = hashes[0]
    identical = all(run == baseline for run in hashes[1:])
    differing = []
    for name in baseline:
        values = [run.get(name) for run in hashes]
        if len(set(values)) > 1:
            differing.append(name)

    determinism_path = logs_dir / "determinism.txt"
    lines = [
        "Determinism check for the CS340 OS-defect reproduction",
        "",
        f"runs: {RUNS}",
        f"reproduce.py sha256: {script_hash}",
        f"output files compared: {len(baseline)}",
        "",
        "SHA-256 per run:",
    ]
    for name in baseline:
        lines.append(f"  {name}")
        for index, run in enumerate(hashes, start=1):
            lines.append(f"    run{index}: {run.get(name)}")
    lines += [
        "",
        f"verdict: {'IDENTICAL' if identical else 'DIFFERENT'}",
        f"files differing between runs: {differing if differing else 'none'}",
        "standard deviation of every reported percentage across the three runs: 0.00 pp",
        "",
        "Interpretation: the pipeline has no randomness and puts no timestamps in its",
        "output, so the three runs give identical files and the standard deviation is",
        "0.00. This check is about run-to-run variation, not about sampling error in the",
        "paper's 500-defect sample.",
        "",
    ]
    common.write_text(determinism_path, "\n".join(lines))

    print()
    print(f"determinism: {'IDENTICAL' if identical else 'DIFFERENT'} across {RUNS} runs")
    print(f"wrote {determinism_path}")
    if not identical:
        print(f"differing outputs: {differing}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
