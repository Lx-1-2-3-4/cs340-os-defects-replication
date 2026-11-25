"""Check the saved study and write evidence from three independent offline runs."""
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET

from analysis import ROOT, within_window
from core import ScratchDirectory


def rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def hashes(directory):
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(directory.iterdir()) if path.is_file()}


def check_tables(directory):
    audit = rows(directory / "candidate_audit.csv")
    defects = rows(directory / "defects.csv")
    if defects != [row for row in audit if row["decision"] == "include"]:
        raise ValueError("Included records do not match the candidate audit")
    keys = {(row["source"], row["defect_id"]) for row in defects}
    if len(keys) != len(defects):
        raise ValueError("Duplicate included identity")
    for row in defects:
        if not all(row[key] for key in ("issue_url", "inspected_diff_sha256", "decision_evidence")):
            raise ValueError(f"Missing evidence for {row['defect_id']}")
        if not all(within_window(row[key]) for key in ("report_date_utc", "fix_date_utc")):
            raise ValueError(f"Date outside the window for {row['defect_id']}")
        added, deleted, changed = [int(row[key]) for key in ("lines_added", "lines_deleted", "lines_changed")]
        if min(added, deleted) < 0 or added + deleted != changed or changed > 500:
            raise ValueError(f"Inconsistent patch size for {row['defect_id']}")
    for name in ("layers.svg", "service_triggers.svg"):
        ET.parse(directory / name)


def main():
    saved = ROOT / "results"
    receipt = saved / "local_verification.json"
    receipt.unlink(missing_ok=True)
    check_tables(saved)
    expected = hashes(saved)
    expected.pop(receipt.name, None)
    runs = []
    with ScratchDirectory(parent=ROOT) as scratch:
        for index in range(1, 4):
            output = Path(scratch) / str(index)
            start = datetime.now(timezone.utc).isoformat()
            process = subprocess.run([sys.executable, "-B", str(ROOT / "analysis.py"),
                                      "--out-dir", str(output)],
                                     check=True, capture_output=True, text=True)
            actual = hashes(output)
            if actual != expected:
                mismatched = sorted(name for name in actual.keys() | expected.keys()
                                    if actual.get(name) != expected.get(name))
                raise ValueError(f"Saved results differ from replay {index}: {', '.join(mismatched)}")
            runs.append(dict(run=index, started_utc=start, returncode=process.returncode,
                             summary=json.loads(process.stdout)))
        verification = dict(python=platform.python_version(), platform=platform.system(), runs=runs,
                            identical_output_sha256=expected,
                            verified=["included cohort matches audit", "identities and evidence links",
                                      "date window and patch ceiling", "SVG structure",
                                      "three byte-identical replays"])
        temporary = Path(scratch) / receipt.name
        temporary.write_text(json.dumps(verification, indent=2) + "\n", encoding="utf-8", newline="\n")
        temporary.replace(receipt)
    print(f"Three offline runs each matched {len(expected)} saved outputs.")


if __name__ == "__main__":
    main()
