#!/usr/bin/env python3
"""Compare the Figure 2 shares with equal total weight per Patch field value.

Run `python extension/patch_link_weighting.py` from the project folder.
The script checks the record-level shares against the reproduction and
writes both sets of shares to `extension/results/patch_link_weighting.csv`.
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import common  # noqa: E402  (path set above)

BUCKET_LABELS = [label for label, _, _ in common.FIG2_BUCKETS]
EXPECTED_PATCH_FIELD_COUNTS = {"android": 473, "linux": 492, "harmony": 487}
RESULTS_CSV = REPO_ROOT / "results" / "fig2_reproduction.csv"


def record_counts(rows):
    """Count records per Figure 2 bucket (each record counts 1)."""
    counts = Counter()
    for row in rows:
        counts[common.bucket_name(row["Line Changes"], common.FIG2_BUCKETS)] += 1
    return counts


def patch_field_weighted_counts(rows):
    """Count weighted defects per bucket, giving each full field value weight 1.

    Returns the bucket weights, the distinct field count, and a histogram
    of how many records share each field value.
    """
    patch_values = []
    for row in rows:
        patch = (row.get("Patch") or "").strip()
        if not patch:
            raise SystemExit(f"empty Patch field for bug {row['Bug ID']}")
        patch_values.append(patch)
    field_counts = Counter(patch_values)
    weights = defaultdict(float)
    for row, patch in zip(rows, patch_values):
        weights[common.bucket_name(row["Line Changes"], common.FIG2_BUCKETS)] += 1.0 / field_counts[patch]
    multiplicities = Counter(field_counts.values())
    return weights, len(field_counts), multiplicities


def check_baseline(records) -> None:
    """Verify the record-level percentages against results/fig2_reproduction.csv."""
    if not RESULTS_CSV.exists():
        raise SystemExit(f"missing {RESULTS_CSV}; run `python scripts/run_triplicate.py` first")
    baseline = {(row["os"], row["bucket"]): row["ours_pct"] for row in common.read_csv(RESULTS_CSV)}
    checked = 0
    mismatches = []
    for tag in common.OS_TAGS:
        rows = records[tag]
        total = len(rows)
        counts = record_counts(rows)
        for label in BUCKET_LABELS:
            key = (tag, label)
            if key not in baseline:
                raise SystemExit(f"missing baseline row {key} in {RESULTS_CSV}")
            ours = common.fmt_pct(100.0 * counts.get(label, 0) / total)
            checked += 1
            if ours != baseline[key]:
                mismatches.append((key, baseline[key], ours))
    if mismatches:
        raise SystemExit("baseline mismatch: " + repr(mismatches))
    print(f"baseline check: {checked}/{checked} record-level bucket percentages match "
          f"results/fig2_reproduction.csv at two decimals")


def main() -> int:
    records = common.load_defects()
    check_baseline(records)

    out_rows = []
    for tag in common.OS_TAGS:
        rows = records[tag]
        total = len(rows)
        record = record_counts(rows)
        weights, patch_field_count, multiplicities = patch_field_weighted_counts(rows)

        expected_fields = EXPECTED_PATCH_FIELD_COUNTS[tag]
        if patch_field_count != expected_fields:
            raise SystemExit(
                f"{tag}: expected {expected_fields} distinct Patch field values, found {patch_field_count} "
                "(the released dataset or the patch column changed)"
            )

        record_total_pct = sum(100.0 * record.get(label, 0) / total for label in BUCKET_LABELS)
        weighted_total_pct = sum(100.0 * weights.get(label, 0.0) / patch_field_count
                                 for label in BUCKET_LABELS)
        if abs(record_total_pct - 100.0) > 1e-9:
            raise SystemExit(f"{tag}: record-level shares sum to {record_total_pct}, not 100")
        if abs(weighted_total_pct - 100.0) > 1e-9:
            raise SystemExit(f"{tag}: field-weighted shares sum to {weighted_total_pct}, not 100")

        print(f"\n{common.OS_DISPLAY[tag]}: {total} records, {patch_field_count} distinct Patch field values")
        print(f"  field multiplicities: "
              + ", ".join(f"{m}x{v}" for m, v in sorted(multiplicities.items())))
        print(f"  record shares sum to {record_total_pct:.6f}%, "
              f"field-weighted shares sum to {weighted_total_pct:.6f}%")

        for label in BUCKET_LABELS:
            record_pct = 100.0 * record.get(label, 0) / total
            weighted_pct = 100.0 * weights.get(label, 0.0) / patch_field_count
            out_rows.append({
                "os": tag,
                "bucket": label,
                "record_pct": common.fmt_pct(record_pct),
                "patch_field_weighted_pct": common.fmt_pct(weighted_pct),
                "delta_pp": f"{weighted_pct - record_pct:+.2f}",
            })
            print(f"    {label:>9}: record {common.fmt_pct(record_pct):>6}%  "
                  f"field-weighted {common.fmt_pct(weighted_pct):>6}%  "
                  f"delta {weighted_pct - record_pct:+.2f} pp")

        top_record = max(BUCKET_LABELS, key=lambda label: record.get(label, 0))
        top_weighted = max(BUCKET_LABELS, key=lambda label: weights.get(label, 0.0))
        largest = max(BUCKET_LABELS, key=lambda label: abs(weights.get(label, 0.0) / patch_field_count
                                                          - record.get(label, 0) / total))
        print(f"  top bucket: record={top_record}, field-weighted={top_weighted}, "
              f"{'unchanged' if top_record == top_weighted else 'CHANGED'}")
        delta_pp = 100.0 * (weights.get(largest, 0.0) / patch_field_count - record.get(largest, 0) / total)
        print(f"  largest absolute change: {largest} {delta_pp:+.2f} pp")

    out_path = REPO_ROOT / "extension" / "results" / "patch_link_weighting.csv"
    common.write_csv(
        out_path,
        ["os", "bucket", "record_pct", "patch_field_weighted_pct", "delta_pp"],
        out_rows,
    )
    print(f"\nwrote {out_path} ({len(out_rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
