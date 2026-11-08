"""Run the whole pipeline three times and check that the output is identical.

The course report asks for mean +/- standard deviation over at least three runs.
The recomputation is deterministic (no sampling, no randomness), so the expected
standard deviation is 0.00; this script proves it instead of asserting it.

Usage:
    python scripts/triplicate.py
"""

from __future__ import annotations

import subprocess
import sys

import common as C

RUNS = 3
FILES = ("table2.csv", "table3.csv", "table4.csv", "table5.csv",
         "fig2.csv", "fig3.csv", "fig4.csv", "comparison.csv", "check.json")


def run_once(index):
    out_dir = C.RESULTS_DIR / "logs" / f"run{index}"
    subprocess.run([sys.executable, str(C.ROOT / "scripts" / "reproduce.py"),
                    "--results", str(out_dir)], check=True,
                   stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, str(C.ROOT / "scripts" / "compare.py"),
                    "--results", str(out_dir)], check=True,
                   stdout=subprocess.DEVNULL)
    return {name: C.sha256_file(out_dir / name) for name in FILES}


def main():
    hashes = [run_once(i) for i in range(1, RUNS + 1)]

    lines = ["# Determinism check", "",
             f"{RUNS} independent runs of reproduce.py + compare.py.", "",
             "| file | " + " | ".join(f"run{i}" for i in range(1, RUNS + 1)) + " | identical |",
             "| --- | " + " | ".join("---" for _ in range(RUNS)) + " | --- |"]
    all_identical = True
    for name in FILES:
        values = [h[name] for h in hashes]
        same = len(set(values)) == 1
        all_identical &= same
        lines.append("| " + name + " | " +
                     " | ".join(v[:12] for v in values) +
                     " | " + ("yes" if same else "NO") + " |")
    lines += ["", f"All outputs identical across {RUNS} runs: "
                  f"{'yes' if all_identical else 'NO'}.", ""]
    C.write_text(C.RESULTS_DIR / "logs" / "determinism.md", "\n".join(lines))
    print("\n".join(lines[-3:]))
    return 0 if all_identical else 1


if __name__ == "__main__":
    sys.exit(main())
