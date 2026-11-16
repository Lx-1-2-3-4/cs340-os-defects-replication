"""Test, audit, run three processes, plot and verify the member contribution."""
from __future__ import annotations
import subprocess
import sys
import core as C
import run_triplicate
import plot_results
import verify_results


def main():
    args = C.arguments(__doc__, runs=True)
    C.invalidate_completion(args.out_dir)
    tests = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", str(C.ROOT/"tests"), "-v"], cwd=C.ROOT)
    if tests.returncode:
        return tests.returncode
    run_triplicate.run(args)
    plot_results.generate(args.out_dir)
    result = verify_results.verify(args.out_dir, args.data_dir, args.paper_dir)
    C.write_json(args.out_dir/"verification.json", result)
    print("ALL LOCAL CHECKS PASSED; this command never commits or uploads anything")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
