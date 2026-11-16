"""Independent preprocessing audit by 1240009531 吴彦阳.

Taxonomy order and paper-reference schemas follow the attributed group baseline
at 91697f2. No teammate analysis module is imported. Standard library only.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import json
import math
import re
import shutil
import uuid
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUP = ROOT.parent
BASELINE_COMMIT = "91697f2eb9ca51105f8c976d266081b9daa1e7be"
DATA = GROUP / "liuxin1240013249" / "data"
SYSTEMS = ("android", "linux", "harmony")
NAMES = {"android": "Android", "linux": "Linux", "harmony": "HarmonyOS"}
PAIRS = (("android", "linux"), ("android", "harmony"), ("linux", "harmony"))
PANELS = {
    "a_os_layer": ("OS Layer", (
        "Kernel Layer", "System Library Layer", "Runtime/Virtual Machine Layer",
        "Framework Layer", "System Service Layer", "Application Layer")),
    "b_affected_function": ("Affected Function", (
        "Memory and Resource Management", "Process and Task Scheduling", "Storage Management",
        "Device Management and Drivers", "Network and Communication", "Compatibility and Adaptation",
        "Security and Permission Control", "Graphics and Rendering")),
    "c_trigger_scenario": ("Trigger Scenario", (
        "Permission/Identity Dependency Trigger", "Regular Operation Trigger", "Boundary Condition Trigger",
        "Concurrency/Multi-thread Trigger", "State Dependency Trigger", "Environment Dependency Trigger",
        "Multi-Language/Localization Trigger")),
}
SEVERITIES = {"Critical", "High", "Medium", "Low", "Undecided", "Unknown"}
CODE_ELEMENTS = {"Entire Class", "Entire Function", "Function Signature", "Loop", "If", "Exception",
                 "Function Call", "Assignment", "Return", "Condition", "Object", "Variable"}
NUMERIC_FIELDS = ("Line Deletions", "Line Additions", "Line Changes", "Involved Functions", "Modified Files")
METRICS = {
    "lines": ("Line Changes", (10, 30, 50, 100), ("0-10", "10-30", "30-50", "50-100", "100-500")),
    "functions": ("Involved Functions", (3, 5, 10), ("0-3", "3-5", "5-10", "10-50")),
    "files": ("Modified Files", (3, 5, 10), ("0-3", "3-5", "5-10", "10-50")),
}


class ScratchDirectory:
    """Owned scratch directory with inherited ACLs, including Windows sandboxes.

    Python's Windows mkdir(mode=0o700), used by tempfile, can remove the ACL
    needed by a restricted process token. A random owned child with ordinary
    inherited permissions also keeps all scratch I/O in the selected workspace.
    """
    def __init__(self, parent=ROOT):
        self.parent = Path(parent).resolve()
        self.path = self.parent/(".cs340-"+uuid.uuid4().hex)
        self.path.mkdir()
        self.name = str(self.path)

    def cleanup(self):
        if self.path.exists():
            if self.path.is_symlink() or self.path.resolve().parent != self.parent:
                raise ValueError("refusing to remove an unowned scratch target")
            shutil.rmtree(self.path)

    def __enter__(self):
        return self.path

    def __exit__(self, *exc):
        self.cleanup()


@dataclass(frozen=True)
class Count:
    lower: int
    censored: bool = False


def parse_count(value) -> Count:
    """A trailing + is a lower bound, not an exact measurement."""
    if isinstance(value, bool):
        raise ValueError("boolean is not a numeric count")
    if isinstance(value, int) and value >= 0:
        return Count(value)
    if isinstance(value, str) and re.fullmatch(r"\d+\+?", value):
        return Count(int(value.rstrip("+")), value.endswith("+"))
    raise ValueError(f"expected a nonnegative integer or lower-bound string, got {value!r}")


def bucket(value, cuts, policy: str) -> int:
    """Return a unique bucket; reject a censored value crossing a cut point."""
    possible = possible_buckets(value, cuts, policy)
    if len(possible) != 1:
        raise ValueError("censored measurement could belong to multiple buckets")
    return possible[0]


def possible_buckets(value, cuts, policy: str) -> tuple:
    """Conservative membership set for exact counts and lower-bound observations."""
    number = parse_count(value)
    if policy not in ("half_open", "right_closed"):
        raise ValueError(f"unknown policy {policy}")
    if tuple(sorted(set(cuts))) != tuple(cuts) or not cuts or cuts[0] <= 0:
        raise ValueError("cuts must be positive and strictly increasing")
    index = (bisect.bisect_right if policy == "half_open" else bisect.bisect_left)(cuts, number.lower)
    return tuple(range(index, len(cuts)+1)) if number.censored else (index,)


def interval(cuts, index, policy):
    if policy == "half_open":
        return f"[{0 if index == 0 else cuts[index-1]},{cuts[index]})" if index < len(cuts) else f"[{cuts[-1]},inf)"
    return f"[0,{cuts[0]}]" if index == 0 else (f"({cuts[index-1]},{cuts[index]}]" if index < len(cuts) else f"({cuts[-1]},inf)")


def ranks(values):
    """Average ranks for ties, implemented independently of the baseline."""
    ordered = sorted(values)
    rank_map = {}
    offset = 0
    for value, frequency in sorted(Counter(ordered).items()):
        rank_map[value] = offset + (frequency + 1) / 2
        offset += frequency
    return [rank_map[value] for value in values]


def spearman(x, y):
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("paired vectors must have equal length >= 2")
    if not all(math.isfinite(v) for v in (*x, *y)):
        raise ValueError("non-finite input")
    a, b = ranks(x), ranks(y)
    center = (len(x) + 1) / 2
    numerator = sum((u-center)*(v-center) for u, v in zip(a, b))
    denominator = math.sqrt(sum((u-center)**2 for u in a) * sum((v-center)**2 for v in b))
    if not denominator:
        raise ValueError("Spearman correlation is undefined for a constant vector")
    return max(-1.0, min(1.0, numerator / denominator))


def strength(value):
    a = abs(value)
    return "very_strong" if a >= .8 else "strong" if a >= .6 else "moderate" if a >= .4 else "weak_or_none"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value.encode("utf-8"))


def write_json(path, value):
    text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_csv(path, fields, values):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(values)


def read_csv(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def invalidate_completion(out):
    """A failed new attempt must not retain an old successful receipt."""
    (Path(out)/"verification.json").unlink(missing_ok=True)


def load(data_dir):
    return {tag: json.loads((Path(data_dir)/f"defects_{tag}.json").read_text(encoding="utf-8")) for tag in SYSTEMS}


def arguments(description, argv=None, runs=False):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--data-dir", type=Path, default=DATA)
    parser.add_argument("--paper-dir", type=Path, help="defaults to DATA_DIR/paper")
    parser.add_argument("--out-dir", type=Path, default=ROOT/"results")
    if runs:
        parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args(argv)
    args.paper_dir = args.paper_dir or args.data_dir/"paper"
    if runs and args.runs < 3:
        parser.error("at least three runs are required")
    # Fail closed before writing if an output directory would contain the inputs.
    out = args.out_dir.resolve()
    for source in (args.data_dir.resolve(), args.paper_dir.resolve()):
        if out == source or out in source.parents or source in out.parents:
            parser.error("input and output directories must not overlap")
    return args
