"""Shared constants and helpers for the CS340 replication of

    Hongyao Zuo, Jiali Li, Jiajun Jiang.
    "Toward Understanding Operating System Defects." arXiv:2608.20643v1, 2026.

The pipeline uses only the Python standard library.  Every path is derived from
the folder that contains this repository, never from a hard-coded absolute path.
"""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PAPER_DIR = DATA_DIR / "paper"
RESULTS_DIR = ROOT / "results"
LOGS_DIR = RESULTS_DIR / "logs"

SYSTEMS = ("android", "linux", "harmony")
SYSTEM_NAME = {"android": "Android", "linux": "Linux", "harmony": "HarmonyOS"}

# ---------------------------------------------------------------------------
# Label vocabularies
#
# The dashboard stores long labels; the paper prints short ones.  These tables
# translate between the two.  Unknown labels raise instead of being ignored.
# ---------------------------------------------------------------------------

LAYER = {
    "Kernel Layer": "Kernel",
    "System Library Layer": "SystemLib",
    "Runtime/Virtual Machine Layer": "RuntimeVM",
    "Framework Layer": "Framework",
    "System Service Layer": "SystemService",
    "Application Layer": "Application",
}

FUNCTION = {
    "Memory and Resource Management": "Mem/Res Mng",
    "Process and Task Scheduling": "Pro/Tas Sch",
    "Storage Management": "Sto Mng",
    "Device Management and Drivers": "Dev/Drv",
    "Network and Communication": "Net/Com",
    "Compatibility and Adaptation": "Com/Adp",
    "Security and Permission Control": "Sec/Perm",
    "Graphics and Rendering": "Gra/Ren",
}

TRIGGER = {
    "Permission/Identity Dependency Trigger": "Per/Ide Dep",
    "Regular Operation Trigger": "Reg Ope",
    "Boundary Condition Trigger": "Bor Con",
    "Concurrency/Multi-thread Trigger": "Con/Mul Thr",
    "State Dependency Trigger": "Sta Dep",
    "Environment Dependency Trigger": "Env Dep",
    "Multi-Language/Localization Trigger": "Mul/Loc Dep",
}

SEVERITY = {
    "Critical": "Critical",
    "High": "High",
    "Medium": "Medium",
    "Low": "Low",
    "Undecided": "Undecided",
    "Unknown": "Undecided",   # six HarmonyOS records, see docs/DEVIATIONS.md
}

# "Code Level" is multi-label, e.g. "Entire Function, If, Function Call".
CODE_ELEMENT = {
    "Entire Class": "Class",
    "Entire Function": "Function",
    "Function Signature": "Signature",
    "Loop": "Loop",
    "If": "If",
    "Exception": "Exception",
    "Function Call": "Call",
    "Assignment": "Assignment",
    "Return": "Return",
    "Condition": "Condition",
    "Object": "Object",
    "Variable": "Variable",
}

# Category order of Table II.  The same order defines the vectors that are
# ranked in Figure 4, so it is kept in one place.
CATEGORY_ORDER = {
    "os_layer": ["Kernel", "SystemLib", "RuntimeVM", "Framework",
                 "SystemService", "Application"],
    "affected_function": ["Mem/Res Mng", "Pro/Tas Sch", "Sto Mng", "Dev/Drv",
                          "Net/Com", "Com/Adp", "Sec/Perm", "Gra/Ren"],
    "trigger_scenario": ["Per/Ide Dep", "Reg Ope", "Bor Con", "Con/Mul Thr",
                         "Sta Dep", "Env Dep", "Mul/Loc Dep"],
    "severity": ["Critical", "High", "Medium", "Low", "Undecided"],
    "code_element": ["Class", "Function", "Signature", "Loop", "If", "Exception",
                     "Call", "Assignment", "Return", "Condition", "Object",
                     "Variable"],
}

TABLE2_PANELS = ("os_layer", "affected_function", "trigger_scenario",
                 "severity", "code_element")

# Row/column order of Tables III-V, as printed (alphabetical).
LAYER_ROWS = ["Application", "Framework", "Kernel", "RuntimeVM", "SystemLib",
              "SystemService"]
FUNCTION_ROWS = ["Com/Adp", "Dev/Drv", "Gra/Ren", "Mem/Res Mng", "Net/Com",
                 "Pro/Tas Sch", "Sec/Perm", "Sto Mng"]
TRIGGER_COLUMNS = ["Per/Ide Dep", "Reg Ope", "Bor Con", "Con/Mul Thr",
                   "Sta Dep", "Env Dep", "Mul/Loc Dep"]

# Histogram buckets read off the printed bar labels.  Half-open except the last.
FIG2_BUCKETS = [("0-10", 0, 10), ("10-30", 10, 30), ("30-50", 30, 50),
                ("50-100", 50, 100), ("100-500", 100, 10 ** 9)]
FIG3_BUCKETS = [("0-3", 0, 3), ("3-5", 3, 5), ("5-10", 5, 10),
                ("10-50", 10, 10 ** 9)]

PAIRS = (("android", "linux"), ("android", "harmony"), ("linux", "harmony"))
FIG4_PANELS = ("a_os_layer", "b_affected_function", "c_trigger_scenario",
               "d_overall")


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def as_int(value):
    """Dashboard numbers are ints, except some HarmonyOS strings like '20+'."""
    if isinstance(value, bool):
        raise TypeError(f"boolean is not a defect count: {value!r}")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value.rstrip("+"))
    raise TypeError(f"unexpected dashboard value: {value!r}")


def bucket_of(value, buckets):
    value = as_int(value)
    for name, low, high in buckets:
        if low <= value < high:
            return name
    raise ValueError(f"{value} is outside the bucket range")


def pct(count):
    """Percentage of the 500 defects of one system, rounded like the paper."""
    return round(count / 5.0, 2)


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_rows(path, fields, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")


def write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def environment():
    return {
        "python": sys.version.split()[0],
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
    }


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

def load_dataset(data_dir=DATA_DIR):
    """Load the three defect files and check that the schema is as expected."""
    data_dir = Path(data_dir)
    data = {}
    for system in SYSTEMS:
        path = data_dir / f"defects_{system}.json"
        if not path.is_file():
            raise FileNotFoundError(f"missing {path}")
        data[system] = json.loads(path.read_text(encoding="utf-8"))
    check_dataset(data)
    return data


def check_dataset(data):
    maps = {"OS Layer": LAYER, "Affected Function": FUNCTION,
            "Trigger Scenario": TRIGGER, "Severity Level": SEVERITY}
    for system, rows in data.items():
        if len(rows) != 500:
            raise ValueError(f"{system}: {len(rows)} records, expected 500")
        if len({row["Bug ID"] for row in rows}) != 500:
            raise ValueError(f"{system}: duplicate Bug IDs")
        for row in rows:
            for field, table in maps.items():
                if row.get(field) not in table:
                    raise ValueError(f"{system}: unknown {field} {row.get(field)!r}")
            for part in row["Code Level"].split(","):
                if part.strip() not in CODE_ELEMENT:
                    raise ValueError(f"{system}: unknown Code Level {part!r}")
            for field in ("Line Changes", "Involved Functions", "Modified Files"):
                as_int(row[field])


def data_hashes(data_dir=DATA_DIR):
    return {f"defects_{s}.json": sha256_file(Path(data_dir) / f"defects_{s}.json")
            for s in SYSTEMS}


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def count_single(rows, field, table):
    return Counter(table[row[field]] for row in rows)


def count_code_elements(rows):
    """A defect counts once for every tag in its comma-separated Code Level."""
    counter = Counter()
    for row in rows:
        for part in row["Code Level"].split(","):
            counter[CODE_ELEMENT[part.strip()]] += 1
    return counter


def panel_counts(data, panel):
    if panel == "os_layer":
        return {s: count_single(rows, "OS Layer", LAYER) for s, rows in data.items()}
    if panel == "affected_function":
        return {s: count_single(rows, "Affected Function", FUNCTION)
                for s, rows in data.items()}
    if panel == "trigger_scenario":
        return {s: count_single(rows, "Trigger Scenario", TRIGGER)
                for s, rows in data.items()}
    if panel == "severity":
        return {s: count_single(rows, "Severity Level", SEVERITY)
                for s, rows in data.items()}
    if panel == "code_element":
        return {s: count_code_elements(rows) for s, rows in data.items()}
    raise ValueError(panel)


def joint_counts(data, row_field, row_table, col_field, col_table):
    out = {}
    for system, rows in data.items():
        counter = Counter()
        for row in rows:
            counter[(row_table[row[row_field]], col_table[row[col_field]])] += 1
        out[system] = counter
    return out


def histogram_counts(data, field, buckets):
    out = {}
    for system, rows in data.items():
        counter = Counter(bucket_of(row[field], buckets) for row in rows)
        out[system] = counter
    return out


def mid_ranks(values):
    """1-based ranks, ties get the average of the positions they span."""
    values = list(values)
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = rank
        i = j + 1
    return ranks


def pearson(x, y):
    n = len(x)
    if n < 2 or n != len(y):
        raise ValueError("pearson needs two vectors of the same length >= 2")
    mx, my = sum(x) / n, sum(y) / n
    numerator = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sx = sum((a - mx) ** 2 for a in x) ** 0.5
    sy = sum((b - my) ** 2 for b in y) ** 0.5
    if sx == 0 or sy == 0:
        raise ValueError("pearson undefined for a constant vector")
    return numerator / (sx * sy)


def spearman(x, y):
    return pearson(mid_ranks(x), mid_ranks(y))


def drop_double_zero(x, y):
    """Remove categories that are zero for both systems of a pair."""
    kept = [(a, b) for a, b in zip(x, y) if a != 0 or b != 0]
    if len(kept) < 2:
        raise ValueError("fewer than two categories left")
    return [a for a, _ in kept], [b for _, b in kept]


def panel_vector(counts_by_system, panel, system):
    """Percentage vector of one panel for one system, in printed column order."""
    counter = counts_by_system[panel][system]
    return [round(counter.get(name, 0) / 5.0, 2) for name in CATEGORY_ORDER[panel]]
