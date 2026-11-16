"""Schema, provenance and numeric consistency audit; never repairs source data."""
from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path
import core as C

ISSUE_FIELDS = ["severity", "code", "os", "bug_ids", "field", "observed", "expected_or_context"]


def audit(records, data_dir):
    issues, checks = [], []

    def issue(severity, code, tag, ids, field, value, expectation):
        issues.append(dict(zip(ISSUE_FIELDS, (severity, code, tag, ids, field, str(value), expectation))))

    provenance = json.loads((Path(data_dir)/"PROVENANCE.json").read_text(encoding="utf-8"))
    for tag in C.SYSTEMS:
        rs = records[tag]
        if not isinstance(rs, list):
            issue("ERROR", "DATASET_TYPE", tag, "", "dataset", type(rs).__name__, "JSON array of defect objects")
            continue
        name = f"defects_{tag}.json"
        expected = provenance["files"][name]["sha256"]
        actual = C.sha(Path(data_dir)/name)
        checks.append({"os": tag, "check": "source_sha256", "observed": actual, "expected": expected, "pass": actual == expected})
        if actual != expected:
            issue("ERROR", "HASH_MISMATCH", tag, "", name, actual, expected)
        checks.append({"os": tag, "check": "record_count", "observed": len(rs), "expected": 500, "pass": len(rs) == 500})
        if len(rs) != 500:
            issue("ERROR", "RECORD_COUNT", tag, "", "records", len(rs), "500 in the selected published snapshot")
        if not all(isinstance(row, dict) for row in rs):
            issue("ERROR", "RECORD_TYPE", tag, "", "record", "non-object", "JSON object")
            continue
        ids = [row.get("Bug ID", "") for row in rs]
        duplicates = [key for key, n in Counter(str(x) for x in ids).items() if n > 1]
        if duplicates:
            issue("ERROR", "DUPLICATE_ID", tag, " | ".join(duplicates), "Bug ID", len(duplicates), "unique within OS")
        patches = defaultdict(list)
        for row in rs:
            bug = str(row.get("Bug ID", ""))
            if not isinstance(row.get("Bug ID"), str) or not bug.strip():
                issue("ERROR", "MISSING_ID", tag, bug, "Bug ID", repr(row.get("Bug ID")), "nonempty string")
            for _, (field, labels) in C.PANELS.items():
                if row.get(field) not in labels:
                    issue("ERROR", "UNKNOWN_LABEL", tag, bug, field, repr(row.get(field)), "one published taxonomy category")
            if not isinstance(row.get("Severity Level"), str) or row.get("Severity Level") not in C.SEVERITIES:
                issue("ERROR", "UNKNOWN_LABEL", tag, bug, "Severity Level", repr(row.get("Severity Level")), "published severity or Unknown")
            code = row.get("Code Level")
            if not isinstance(code, str) or not code:
                issue("ERROR", "INVALID_CODE_TAGS", tag, bug, "Code Level", repr(code), "nonempty comma-separated labels")
            else:
                tags = [x.strip() for x in code.split(",")]
                if set(tags) - C.CODE_ELEMENTS:
                    issue("ERROR", "UNKNOWN_CODE_TAG", tag, bug, "Code Level", code, "published code-element vocabulary")
                if len(tags) != len(set(tags)):
                    issue("WARN", "REPEATED_CODE_TAG", tag, bug, "Code Level", code, "one occurrence per tag per defect")
            numbers = {}
            for field in C.NUMERIC_FIELDS:
                try:
                    numbers[field] = C.parse_count(row.get(field))
                    if numbers[field].censored:
                        issue("INFO", "LOWER_BOUND_COUNT", tag, bug, field, row[field], "lower bound; only classify if bucket is unambiguous")
                except ValueError as exc:
                    issue("ERROR", "INVALID_COUNT", tag, bug, field, repr(row.get(field)), str(exc))
            if all(f in numbers and not numbers[f].censored for f in C.NUMERIC_FIELDS[:3]):
                removed, added, changed = (numbers[f].lower for f in C.NUMERIC_FIELDS[:3])
                if removed + added != changed:
                    issue("WARN", "LINE_SUM_MISMATCH", tag, bug, "Line Changes", changed,
                          f"{removed} deletions + {added} additions = {removed+added}; verify measurement definition, do not auto-correct")
            for field, code in (("Involved Functions", "ZERO_FUNCTIONS"), ("Modified Files", "ZERO_FILES")):
                if field in numbers and numbers[field].lower == 0 and not numbers[field].censored:
                    issue("INFO" if field == "Involved Functions" else "WARN", code, tag, bug, field, "0",
                          "requires interpretation; globals/configuration can legitimately involve no functions")
            if "Line Changes" in numbers and numbers["Line Changes"].lower > 500:
                issue("WARN", "ABOVE_SELECTION_CAP", tag, bug, "Line Changes", row["Line Changes"], "paper filters repairs above 500 changed lines")
            for metric, (field, cuts, _) in C.METRICS.items():
                if field not in numbers:
                    continue
                for policy in ("half_open", "right_closed"):
                    try:
                        C.bucket(row[field], cuts, policy)
                    except ValueError as exc:
                        issue("ERROR" if policy == "half_open" else "WARN", "AMBIGUOUS_BUCKET" if policy == "half_open" else "AMBIGUOUS_ALTERNATIVE_BUCKET",
                              tag, bug, field, row[field], f"{policy}: {exc}; report bounds, never impute the lower bound as exact")
            patch = row.get("Patch")
            if not isinstance(patch, str) or not patch.strip():
                issue("ERROR", "MISSING_PATCH", tag, bug, "Patch", repr(patch), "nonempty source field")
            else:
                patches[patch.strip()].append(bug)
        for patch, bug_ids in sorted(patches.items()):
            if len(bug_ids) > 1:
                issue("INFO", "SHARED_PATCH_FIELD", tag, " | ".join(bug_ids), "Patch", patch,
                      "shared full field; not necessarily duplicate defects or one independent patch entity")
        checks.append({"os": tag, "check": "unique_bug_ids", "observed": len(set(str(x) for x in ids)), "expected": len(rs), "pass": not duplicates})
    summary = {
        "severity_counts": {key: sum(i["severity"] == key for i in issues) for key in ("ERROR", "WARN", "INFO")},
        "issue_code_counts": dict(sorted(Counter(i["code"] for i in issues).items())),
        "records_per_os": {tag: len(records[tag]) if isinstance(records[tag], list) else None for tag in C.SYSTEMS},
        "source_data_modified": False,
    }
    return issues, checks, summary


def save(records, data_dir, out_dir):
    C.invalidate_completion(out_dir)
    issues, checks, summary = audit(records, data_dir)
    C.write_csv(Path(out_dir)/"data_audit.csv", ISSUE_FIELDS, issues)
    C.write_csv(Path(out_dir)/"audit_checks.csv", ["os", "check", "observed", "expected", "pass"], checks)
    C.write_json(Path(out_dir)/"audit_summary.json", summary)
    return summary


def main():
    args = C.arguments(__doc__)
    summary = save(C.load(args.data_dir), args.data_dir, args.out_dir)
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
    return int(summary["severity_counts"]["ERROR"] > 0)


if __name__ == "__main__":
    raise SystemExit(main())
