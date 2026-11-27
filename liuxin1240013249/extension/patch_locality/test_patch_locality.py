#!/usr/bin/env python3
"""Unit tests for the patch-locality extension (stdlib only, offline)."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

EXT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EXT_DIR.parents[1]
sys.path.insert(0, str(EXT_DIR))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import analysis  # noqa: E402
import common  # noqa: E402


class TestPatchLocality(unittest.TestCase):
    def test_size_buckets_non_overlapping(self):
        ranges = [(lo, hi) for _, lo, hi in analysis.SIZE_BUCKETS]
        for i in range(len(ranges) - 1):
            self.assertEqual(ranges[i][1], ranges[i + 1][0])
        self.assertEqual(analysis.assign_size_bucket(1), "1-9")
        self.assertEqual(analysis.assign_size_bucket(9), "1-9")
        self.assertEqual(analysis.assign_size_bucket(10), "10-29")
        self.assertEqual(analysis.assign_size_bucket(500), "100-500")
        self.assertEqual(analysis.assign_size_bucket(501), "501-1000")
        self.assertEqual(analysis.assign_size_bucket(1000), "501-1000")

    def test_file_category_classification(self):
        self.assertEqual(analysis.classify_file_category("src/core/namespace.c"), "production")
        self.assertEqual(
            analysis.classify_file_category("test/unittest/huks_standard_test/src/foo_test.cpp"),
            "test",
        )
        self.assertEqual(analysis.classify_file_category("testsuites/unittest/container/It_test.cpp"), "test")
        self.assertEqual(analysis.classify_file_category("man/systemd.exec.xml"), "doc")
        self.assertEqual(analysis.classify_file_category("docs/README.md"), "doc")
        self.assertEqual(analysis.classify_file_category("debian/changelog"), "packaging_or_generated")

    def test_module_mapping_distinguishes_files_from_modules(self):
        # Multiple files inside the same systemd/core module -> 2 files, 1 module
        same_mod_files = [
            {"filepath": "src/core/exec-invoke.c", "additions": 10, "deletions": 2},
            {"filepath": "src/core/execute-serialize.c", "additions": 8, "deletions": 1},
            {"filepath": "test/units/TEST-01.sh", "additions": 50, "deletions": 0},
        ]
        m1 = analysis.compute_patch_locality_metrics("Linux", "systemd/systemd", same_mod_files)
        self.assertEqual(m1["raw_files_changed"], 3)
        self.assertEqual(m1["prod_files_changed"], 2)
        self.assertEqual(m1["prod_modules_touched"], 1)
        self.assertFalse(m1["is_cross_module"])
        self.assertEqual(m1["primary_module"], "systemd/core")
        self.assertEqual(m1["primary_module_share"], 1.0)

        # Files across two distinct modules -> cross-module True
        cross_mod_files = [
            {"filepath": "src/core/namespace.c", "additions": 100, "deletions": 10},
            {"filepath": "src/shared/dissect-image.c", "additions": 300, "deletions": 5},
        ]
        m2 = analysis.compute_patch_locality_metrics("Linux", "systemd/systemd", cross_mod_files)
        self.assertEqual(m2["prod_modules_touched"], 2)
        self.assertTrue(m2["is_cross_module"])
        self.assertEqual(m2["primary_module"], "systemd/shared")

    def test_baseline_arithmetic_anomaly_detected(self):
        records = common.load_defects(analysis.BASELINE_DATA_DIR)
        _, anomalies, _ = analysis.analyze_full_baseline(records)
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["bug_id"], "2044216")
        self.assertEqual(anomalies[0]["sum_add_del"], 359)
        self.assertEqual(anomalies[0]["line_changes_reported"], 349)

    def test_deterministic_outputs(self):
        results_dir = EXT_DIR / "results"
        tracked = [
            "merged_dataset.csv",
            "baseline_size_locality.csv",
            "cohort_comparison.csv",
            "module_mapping.csv",
            "candidate_audit.csv",
            "size_vs_scope.svg",
            "summary.json",
            "REPORT.md",
        ]
        before = {
            name: hashlib.sha256((results_dir / name).read_bytes()).hexdigest()
            for name in tracked
        }
        self.assertEqual(analysis.main(), 0)
        after = {
            name: hashlib.sha256((results_dir / name).read_bytes()).hexdigest()
            for name in tracked
        }
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
