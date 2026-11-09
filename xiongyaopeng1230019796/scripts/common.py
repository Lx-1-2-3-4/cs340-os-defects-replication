"""Shared constants and helpers for the CS340 replication of

    Hongyao Zuo, Jiali Li, Jiajun Jiang.
    "Toward Understanding Operating System Defects." arXiv:2608.20643v1, 2026.

The whole pipeline uses only the Python standard library so that it can be run
on a clean machine (or in the pinned Docker image) without third-party wheels.

No absolute paths are hard-coded here: every directory is derived from the
repository root and can be overridden from the command line.
"""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = REPO_ROOT / "data"
DEFAULT_PAPER_DIR = DEFAULT_DATA_DIR / "paper"
DEFAULT_RESULTS_DIR = REPO_ROOT / "results"

OS_TAGS = ("android", "linux", "harmony")
OS_DISPLAY = {"android": "Android", "linux": "Linux", "harmony": "HarmonyOS"}

# ---------------------------------------------------------------------------
# Label vocabularies
#
# The released dashboard uses long English labels; the paper's tables use short
# ones. The dictionaries below translate between the two (see data/README.md).
# An unknown label raises an error instead of being skipped.
# ---------------------------------------------------------------------------

OS_LAYER_LABEL = {
    "Kernel Layer": "Kernel",
    "System Library Layer": "SystemLib",
    "Runtime/Virtual Machine Layer": "RuntimeVM",
    "Framework Layer": "Framework",
    "System Service Layer": "SystemService",
    "Application Layer": "Application",
}

AFFECTED_FUNCTION_LABEL = {
    "Memory and Resource Management": "Mem/Res Mng",
    "Process and Task Scheduling": "Pro/Tas Sch",
    "Storage Management": "Sto Mng",
    "Device Management and Drivers": "Dev/Drv",
    "Network and Communication": "Net/Com",
    "Compatibility and Adaptation": "Com/Adp",
    "Security and Permission Control": "Sec/Perm",
    "Graphics and Rendering": "Gra/Ren",
}

TRIGGER_LABEL = {
    "Permission/Identity Dependency Trigger": "Per/Ide Dep",
    "Regular Operation Trigger": "Reg Ope",
    "Boundary Condition Trigger": "Bor Con",
    "Concurrency/Multi-thread Trigger": "Con/Mul Thr",
    "State Dependency Trigger": "Sta Dep",
    "Environment Dependency Trigger": "Env Dep",
    "Multi-Language/Localization Trigger": "Mul/Loc Dep",
}

# The dashboard stores "Unknown" for six HarmonyOS records; the paper reports
# them under "Undecided".  Linux uses "Undecided" directly.
SEVERITY_LABEL = {
    "Critical": "Critical",
    "High": "High",
    "Medium": "Medium",
    "Low": "Low",
    "Undecided": "Undecided",
    "Unknown": "Undecided",
}

# "Code Level" is a multi-label field: e.g. "Entire Function, If, Function Call".
CODE_ELEMENT_LABEL = {
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

# Column order used in the paper's Table II. The same order is used when the
# category vectors for Figure 4 are built.
PANEL_COLUMNS = {
    "os_layer": ["Kernel", "SystemLib", "RuntimeVM", "Framework", "SystemService", "Application"],
    "affected_function": [
        "Mem/Res Mng", "Pro/Tas Sch", "Sto Mng", "Dev/Drv",
        "Net/Com", "Com/Adp", "Sec/Perm", "Gra/Ren",
    ],
    "trigger_scenario": [
        "Per/Ide Dep", "Reg Ope", "Bor Con", "Con/Mul Thr",
        "Sta Dep", "Env Dep", "Mul/Loc Dep",
    ],
    "severity": ["Critical", "High", "Medium", "Low", "Undecided"],
    "code_element": [
        "Class", "Function", "Signature", "Loop", "If", "Exception",
        "Call", "Assignment", "Return", "Condition", "Object", "Variable",
    ],
}

TABLE2_PANELS = ("os_layer", "affected_function", "trigger_scenario", "severity", "code_element")

# Rows of Tables III and IV (paper labels), rows of Table V (paper labels).
LAYER_ROWS = ["Application", "Framework", "Kernel", "RuntimeVM", "SystemLib", "SystemService"]
FUNCTION_ROWS = ["Com/Adp", "Dev/Drv", "Gra/Ren", "Mem/Res Mng", "Net/Com", "Pro/Tas Sch", "Sec/Perm", "Sto Mng"]
TRIGGER_COLUMNS = ["Per/Ide Dep", "Reg Ope", "Bor Con", "Con/Mul Thr", "Sta Dep", "Env Dep", "Mul/Loc Dep"]

# Figure 2 and Figure 3 histogram buckets, reconstructed from the paper's
# figure assets; intervals are half-open [low, high) except the last bucket.
FIG2_BUCKETS = [("0-10", 0, 10), ("10-30", 10, 30), ("30-50", 30, 50),
                ("50-100", 50, 100), ("100-500", 100, 10 ** 9)]
FIG3_BUCKETS = [("0-3", 0, 3), ("3-5", 3, 5), ("5-10", 5, 10), ("10-50", 10, 10 ** 9)]

PAIRS = (("android", "linux"), ("android", "harmony"), ("linux", "harmony"))

REQUIRED_FIELDS = (
    "Bug ID", "Severity Level", "OS Layer", "Affected Function",
    "Trigger Scenario", "Code Level",
)

NUMERIC_FIELDS = ("Line Deletions", "Line Additions", "Line Changes",
                  "Involved Functions", "Modified Files")


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------

def sha256_file(path) -> str:
    """Return the hexadecimal SHA-256 of a file's bytes."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def numeric(value):
    """Convert a dashboard value to int.

    HarmonyOS stores some ``Involved Functions`` values as strings, including
    capped values such as ``"20+"``.  Those are parsed as the integer prefix;
    the cap only affects the open-ended last histogram bucket, so the bucket is
    unaffected.
    """
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value.rstrip("+"))
    raise TypeError(f"not a numeric dashboard value: {value!r}")


def bucket_name(value, buckets):
    """Return the bucket label for ``value`` given ``(label, low, high)`` buckets."""
    value = numeric(value)
    for label, low, high in buckets:
        if low <= value < high:
            return label
    raise ValueError(f"value {value!r} falls outside all buckets")


def fmt_pct(value: float) -> str:
    """Format a percentage exactly like the paper's tables (two decimals)."""
    return f"{value:.2f}"


def fmt_rho(value: float) -> str:
    """Format a correlation coefficient exactly like the paper's heatmaps."""
    return f"{value:.2f}"


def write_text(path, text: str) -> None:
    """Write UTF-8 text with Unix newlines on every platform.

    ``Path.write_text`` translates ``\n`` to ``os.linesep`` on Windows, which
    would make the committed results platform-dependent.  Writing the encoded
    bytes keeps the files byte-identical on Windows, Linux and macOS.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def write_csv(path, fieldnames, rows) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_csv(path):
    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def environment_info() -> dict:
    """Describe the machine that produced a run (recorded in results/)."""
    return {
        "python_version": sys.version.split()[0],
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
    }


# ---------------------------------------------------------------------------
# Dataset loading and validation
# ---------------------------------------------------------------------------

def load_defects(data_dir=DEFAULT_DATA_DIR) -> dict:
    """Load ``data/defects_<os>.json`` for the three systems and validate it."""
    data_dir = Path(data_dir)
    records = {}
    for tag in OS_TAGS:
        path = data_dir / f"defects_{tag}.json"
        if not path.exists():
            raise FileNotFoundError(
                f"missing dataset file {path}; run `python scripts/fetch_data.py` first"
            )
        records[tag] = json.loads(path.read_text(encoding="utf-8"))
    validate_defects(records)
    return records


def validate_defects(records) -> None:
    """Raise on schema drift or unexpected labels."""
    label_maps = {
        "OS Layer": OS_LAYER_LABEL,
        "Affected Function": AFFECTED_FUNCTION_LABEL,
        "Trigger Scenario": TRIGGER_LABEL,
        "Severity Level": SEVERITY_LABEL,
    }
    for tag in OS_TAGS:
        rows = records[tag]
        if len(rows) != 500:
            raise ValueError(f"{tag}: expected 500 records, found {len(rows)}")
        ids = [row.get("Bug ID") for row in rows]
        if len(set(ids)) != len(ids):
            raise ValueError(f"{tag}: duplicate Bug IDs")
        for row in rows:
            for field in REQUIRED_FIELDS:
                if field not in row or row[field] in (None, ""):
                    raise ValueError(f"{tag}: record without {field!r}: {row.get('Bug ID')}")
            for field, mapping in label_maps.items():
                if row[field] not in mapping:
                    raise ValueError(f"{tag}: unseen {field} label {row[field]!r}")
            for piece in row["Code Level"].split(","):
                if piece.strip() not in CODE_ELEMENT_LABEL:
                    raise ValueError(f"{tag}: unseen Code Level label {piece!r}")


def data_sha256(data_dir=DEFAULT_DATA_DIR) -> dict:
    data_dir = Path(data_dir)
    return {f"defects_{tag}.json": sha256_file(data_dir / f"defects_{tag}.json")
            for tag in OS_TAGS}


# ---------------------------------------------------------------------------
# Distributions from the released records
# ---------------------------------------------------------------------------

def single_label_distribution(rows, field, mapping) -> Counter:
    counts = Counter()
    for row in rows:
        counts[mapping[row[field]]] += 1
    return counts


def code_element_counts(rows) -> Counter:
    """Multi-label count: one defect can contribute to several code elements."""
    counts = Counter()
    for row in rows:
        for piece in row["Code Level"].split(","):
            counts[CODE_ELEMENT_LABEL[piece.strip()]] += 1
    return counts


def panel_counts(records, panel) -> dict:
    """Return ``{os_tag: Counter(category -> defect count)}`` for a Table II panel."""
    if panel == "os_layer":
        return {tag: single_label_distribution(rows, "OS Layer", OS_LAYER_LABEL)
                for tag, rows in records.items()}
    if panel == "affected_function":
        return {tag: single_label_distribution(rows, "Affected Function", AFFECTED_FUNCTION_LABEL)
                for tag, rows in records.items()}
    if panel == "trigger_scenario":
        return {tag: single_label_distribution(rows, "Trigger Scenario", TRIGGER_LABEL)
                for tag, rows in records.items()}
    if panel == "severity":
        return {tag: single_label_distribution(rows, "Severity Level", SEVERITY_LABEL)
                for tag, rows in records.items()}
    if panel == "code_element":
        return {tag: code_element_counts(rows) for tag, rows in records.items()}
    raise ValueError(f"unknown panel {panel!r}")


def joint_counts(records, row_field, row_mapping, col_field, col_mapping) -> dict:
    """Return ``{os_tag: {(row_label, col_label): count}}`` for a joint table."""
    out = {}
    for tag, rows in records.items():
        counts = Counter()
        for row in rows:
            counts[(row_mapping[row[row_field]], col_mapping[row[col_field]])] += 1
        out[tag] = counts
    return out


# ---------------------------------------------------------------------------
# Ranking statistics (dependency-free implementation of Spearman's rho)
# ---------------------------------------------------------------------------

def average_ranks(values):
    """Return mid-ranks (1-based) with ties receiving their average rank."""
    values = list(values)
    order = sorted(range(len(values)), key=lambda i: (values[i], i))
    ranks = [0.0] * len(values)
    index = 0
    while index < len(order):
        end = index
        while end + 1 < len(order) and values[order[end + 1]] == values[order[index]]:
            end += 1
        rank = (index + end) / 2.0 + 1.0
        for position in range(index, end + 1):
            ranks[order[position]] = rank
        index = end + 1
    return ranks


def pearson(x, y) -> float:
    n = len(x)
    if n != len(y) or n < 2:
        raise ValueError("pearson needs two equal-length vectors of length >= 2")
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    numerator = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y))
    denominator = (sum((a - mean_x) ** 2 for a in x) * sum((b - mean_y) ** 2 for b in y)) ** 0.5
    if denominator == 0:
        raise ValueError("pearson is undefined for a constant vector")
    return numerator / denominator


def spearman(x, y) -> float:
    return pearson(average_ranks(x), average_ranks(y))


def drop_shared_zeros(x, y):
    """Remove categories that are zero for *both* systems.

    This rule is needed to reproduce panel (c) of the paper's Figure 4: for
    Android-HarmonyOS the 'Mul/Loc Dep' trigger is 0 in both systems and the
    paper appears to drop such categories before ranking (see
    docs/DEVIATIONS.md, deviation D4).
    """
    kept = [(a, b) for a, b in zip(x, y) if not (a == 0 and b == 0)]
    if len(kept) < 2:
        raise ValueError("not enough categories left after dropping shared zeros")
    return [a for a, _ in kept], [b for _, b in kept]


# ---------------------------------------------------------------------------
# Paper values (transcribed, machine-readable copies of the paper's tables and
# figures; see data/paper/README.md for provenance)
# ---------------------------------------------------------------------------

def load_paper_values(paper_dir=DEFAULT_PAPER_DIR) -> dict:
    paper_dir = Path(paper_dir)
    return {
        "table2": read_csv(paper_dir / "table2.csv"),
        "table3": read_csv(paper_dir / "table3.csv"),
        "table4": read_csv(paper_dir / "table4.csv"),
        "table5": read_csv(paper_dir / "table5.csv"),
        "fig2": read_csv(paper_dir / "fig2.csv"),
        "fig3": read_csv(paper_dir / "fig3.csv"),
        "fig4": read_csv(paper_dir / "fig4.csv"),
    }
