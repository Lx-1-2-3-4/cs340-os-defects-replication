"""Hand-checkable rules, conservation properties and adversarial evidence checks."""
from __future__ import annotations
import copy
import json
import math
import shutil
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
import core as C
import audit_data
import run_sensitivity as S
import run_triplicate
import plot_results
import verify_results


class NumericRules(unittest.TestCase):
    def test_exact_and_censored(self):
        self.assertEqual(C.parse_count(0), C.Count(0))
        self.assertEqual(C.parse_count("20+"), C.Count(20, True))
        self.assertEqual(C.parse_count("3"), C.Count(3))

    def test_invalid_numeric_types(self):
        for value in (True, False, -1, 1.2, None, "", "-2", "2.5", "++20", "20++"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                C.parse_count(value)

    def test_every_endpoint(self):
        cuts = (10, 30, 50, 100)
        for i, cut in enumerate(cuts):
            self.assertEqual(C.bucket(cut, cuts, "half_open"), i+1)
            self.assertEqual(C.bucket(cut, cuts, "right_closed"), i)
            self.assertEqual(C.bucket(cut-1, cuts, "half_open"), i)
            self.assertEqual(C.bucket(cut+1, cuts, "right_closed"), i+1)

    def test_zero_and_tail(self):
        for policy in ("half_open", "right_closed"):
            self.assertEqual(C.bucket(0, (3, 5, 10), policy), 0)
            self.assertEqual(C.bucket("20+", (3, 5, 10), policy), 3)
            self.assertEqual(C.bucket(1000000, (3, 5, 10), policy), 3)

    def test_ambiguous_censoring_is_rejected(self):
        for policy in ("half_open", "right_closed"):
            with self.assertRaises(ValueError):
                C.bucket("3+", (3, 5, 10), policy)
        self.assertEqual(C.bucket("10+", (3, 5, 10), "half_open"), 3)
        with self.assertRaises(ValueError):
            C.bucket("10+", (3, 5, 10), "right_closed")

    def test_bad_policy_and_cutpoints(self):
        for cuts in ((3, 3), (5, 3), (0, 3), ()):
            with self.assertRaises(ValueError):
                C.bucket(1, cuts, "half_open")
        with self.assertRaises(ValueError):
            C.bucket(1, (3, 5), "unknown")

    def test_average_ties_by_hand(self):
        self.assertEqual(C.ranks([30, 10, 10, 20]), [4, 1.5, 1.5, 3])

    def test_positive_and_negative_rank_correlation(self):
        self.assertAlmostEqual(C.spearman([1, 2, 3], [10, 20, 30]), 1)
        self.assertAlmostEqual(C.spearman([1, 2, 3], [30, 20, 10]), -1)

    def test_tied_correlation_by_hand(self):
        self.assertAlmostEqual(C.spearman([1, 1, 2], [1, 2, 3]), math.sqrt(3)/2)

    def test_undefined_and_invalid_vectors(self):
        for x, y in (([1], [2]), ([1, 2], [1]), ([1, 1], [2, 3]), ([math.nan, 2], [1, 2])):
            with self.assertRaises(ValueError):
                C.spearman(x, y)

    def test_strength_uses_absolute_value_and_exact_thresholds(self):
        self.assertEqual(C.strength(-.66), "strong")
        self.assertEqual(C.strength(.4), "moderate")
        self.assertEqual(C.strength(.8), "very_strong")
        self.assertEqual(C.strength(.3999), "weak_or_none")


class PublishedSnapshot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = C.load(C.DATA)

    def test_no_blocking_error_but_known_arithmetic_warning(self):
        issues, checks, summary = audit_data.audit(self.records, C.DATA)
        self.assertEqual(summary["severity_counts"]["ERROR"], 0)
        self.assertTrue(all(row["pass"] for row in checks))
        self.assertEqual([(r["os"], r["bug_ids"], r["observed"]) for r in issues if r["code"] == "LINE_SUM_MISMATCH"], [("linux", "2044216", "349")])

    def test_invalid_record_is_blocking(self):
        modified = copy.deepcopy(self.records)
        modified["android"][0]["Line Changes"] = -1
        modified["android"][1]["Bug ID"] = modified["android"][0]["Bug ID"]
        issues, _, summary = audit_data.audit(modified, C.DATA)
        self.assertGreater(summary["severity_counts"]["ERROR"], 0)
        self.assertIn("INVALID_COUNT", {r["code"] for r in issues})
        self.assertIn("DUPLICATE_ID", {r["code"] for r in issues})

    def test_nonarray_dataset_is_reported_not_crashed(self):
        modified = dict(self.records)
        modified["android"] = None
        issues, _, summary = audit_data.audit(modified, C.DATA)
        self.assertIn("DATASET_TYPE", {r["code"] for r in issues})
        self.assertIsNone(summary["records_per_os"]["android"])

    def test_zero_functions_are_informational(self):
        issues, _, _ = audit_data.audit(self.records, C.DATA)
        zeros = [r for r in issues if r["code"] == "ZERO_FUNCTIONS"]
        self.assertEqual(len(zeros), 177)
        self.assertTrue(all(r["severity"] == "INFO" for r in zeros))

    def test_full_and_filtered_correlation_contrast(self):
        rows, vectors, metrics = S.zero_experiment(self.records, C.DATA/"paper")
        self.assertEqual(len(rows), 9)
        self.assertEqual(len(vectors), 63)
        self.assertEqual(len(metrics), 18)
        target = next(r for r in rows if r["panel"] == "c_trigger_scenario" and r["pair"] == "android-harmony")
        self.assertAlmostEqual(float(target["all_rho"]), .6126374746329801)
        self.assertAlmostEqual(float(target["drop_rho"]), .3768511731740915)
        self.assertEqual((target["all_categories"], target["nonsharedzero_categories"]), (7, 6))
        self.assertEqual(sum(r["strength_changed"] for r in rows), 1)

    def test_bin_conservation_and_boundary_explanation(self):
        rows, memberships, metrics, overview = S.bin_experiment(self.records, C.DATA/"paper")
        self.assertEqual((len(rows), len(memberships), len(metrics)), (39, 4500, 117))
        for tag in C.SYSTEMS:
            for metric, (_, cuts, _) in C.METRICS.items():
                selected = [r for r in rows if r["os"] == tag and r["metric"] == metric]
                self.assertEqual(sum(r["half_open_count"] for r in selected), 500)
                self.assertLessEqual(sum(r["right_closed_count_min"] for r in selected), 500)
                self.assertGreaterEqual(sum(r["right_closed_count_max"] for r in selected), 500)
                for record in (r for r in memberships if r["os"] == tag and r["metric"] == metric):
                    if not record["censored"]:
                        self.assertEqual(record["movement"] == "moved", C.parse_count(record["source_value"]).lower in cuts)
        target = next(r for r in rows if r["os"] == "linux" and r["metric"] == "files" and r["bucket_index"] == 0)
        self.assertEqual((target["half_open_count"], target["right_closed_count"]), (312, 384))
        self.assertTrue(all(r["top_set_unchanged"] for r in overview))

    def test_lower_bound_ten_plus_is_not_silently_imputed(self):
        rows, membership, _, _ = S.bin_experiment(self.records, C.DATA/"paper")
        uncertain = [r for r in membership if r["movement"] == "possible"]
        self.assertEqual(len(uncertain), 3)
        target = next(r for r in rows if r["os"] == "harmony" and r["metric"] == "functions" and r["bucket_index"] == 2)
        self.assertEqual((target["right_closed_count_min"], target["right_closed_count_max"]), (27, 30))
        self.assertEqual(target["right_closed_pct"], "")


class EvidenceVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = C.ScratchDirectory(parent=ROOT)
        cls.addClassCleanup(cls.temp.cleanup)
        cls.results = Path(cls.temp.name)/"results"
        args = SimpleNamespace(data_dir=C.DATA, paper_dir=C.DATA/"paper", out_dir=cls.results, runs=3)
        run_triplicate.run(args)
        plot_results.generate(cls.results)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.copy = C.ScratchDirectory(parent=ROOT)
        self.out = Path(self.copy.name)/"results"
        shutil.copytree(self.results, self.out)

    def tearDown(self):
        self.copy.cleanup()

    def test_full_evidence_verifies(self):
        result = verify_results.verify(self.out, C.DATA, C.DATA/"paper")
        self.assertEqual((result["runs"], result["metric_count"]), (3, 135))

    def test_changed_cell_fails_even_with_unchanged_totals(self):
        p = self.out/"binning_comparison.csv"
        rows = C.read_csv(p)
        rows[0]["half_open_pct"] = "35.00000000"
        C.write_csv(p, list(rows[0]), rows)
        with self.assertRaisesRegex(ValueError, "binning_comparison.csv"):
            verify_results.verify(self.out, C.DATA, C.DATA/"paper")

    def test_changed_run_metric_fails(self):
        p = self.out/"runs/run2_metrics.csv"
        rows = C.read_csv(p)
        rows[0]["value"] = "0.99"
        C.write_csv(p, list(rows[0]), rows)
        with self.assertRaisesRegex(ValueError, "run 2"):
            verify_results.verify(self.out, C.DATA, C.DATA/"paper")

    def test_false_mean_is_rejected(self):
        p = self.out/"run_statistics.csv"
        rows = C.read_csv(p)
        rows[0]["mean"] = "0.99"
        C.write_csv(p, list(rows[0]), rows)
        with self.assertRaisesRegex(ValueError, "statistics value mismatch"):
            verify_results.verify(self.out, C.DATA, C.DATA/"paper")

    def test_stale_chart_is_rejected(self):
        p = self.out/"figures/zero_policy.svg"
        p.write_text(p.read_text(encoding="utf-8").replace("0.613", "0.999"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "stale presentation artifact"):
            verify_results.verify(self.out, C.DATA, C.DATA/"paper")

    def test_stale_paper_comparison_is_rejected(self):
        p = self.out/"paper_vs_ours.csv"
        rows = C.read_csv(p)
        rows[0]["paper"] = "0.99"
        C.write_csv(p, list(rows[0]), rows)
        with self.assertRaisesRegex(ValueError, "stale presentation artifact: paper_vs_ours.csv"):
            verify_results.verify(self.out, C.DATA, C.DATA/"paper")

    def test_changed_execution_log_is_rejected(self):
        (self.out/"logs/run1.log").write_text("", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "execution log hash mismatch"):
            verify_results.verify(self.out, C.DATA, C.DATA/"paper")

    def test_old_success_receipt_invalidated_before_failed_verification(self):
        receipt = self.out/"verification.json"
        C.write_json(receipt, {"verified": True})
        rows = C.read_csv(self.out/"run_statistics.csv")
        rows[0]["mean"] = "0.99"
        C.write_csv(self.out/"run_statistics.csv", list(rows[0]), rows)
        with self.assertRaises(ValueError):
            verify_results.verify(self.out, C.DATA, C.DATA/"paper")
        self.assertFalse(receipt.exists())

    def test_standalone_audit_invalidates_previous_success(self):
        C.write_json(self.out/"verification.json", {"verified": True})
        records = C.load(C.DATA)
        records["android"][0]["Line Changes"] = -1
        summary = audit_data.save(records, C.DATA, self.out)
        self.assertGreater(summary["severity_counts"]["ERROR"], 0)
        self.assertFalse((self.out/"verification.json").exists())

    def test_extra_run_evidence_is_rejected(self):
        shutil.copy2(self.out/"runs/run1_metrics.csv", self.out/"runs/run4_metrics.csv")
        with self.assertRaisesRegex(ValueError, "extra or missing run artifacts"):
            verify_results.verify(self.out, C.DATA, C.DATA/"paper")

    def test_rerun_removes_only_owned_artifacts(self):
        shutil.copy2(self.out/"runs/run1_metrics.csv", self.out/"runs/run4_metrics.csv")
        keep = self.out/"logs/personal-notes.txt"
        keep.write_text("keep this", encoding="utf-8")
        C.write_json(self.out/"verification.json", {"verified": True})
        run_triplicate.prepare_output(self.out)
        self.assertFalse((self.out/"runs/run4_metrics.csv").exists())
        self.assertFalse((self.out/"verification.json").exists())
        self.assertFalse((self.out/"REPORT.html").exists())
        self.assertEqual(keep.read_text(encoding="utf-8"), "keep this")

    def test_invalid_elapsed_time_is_rejected(self):
        path = self.out/"logs/run2.json"
        meta = json.loads(path.read_text(encoding="utf-8"))
        meta["elapsed_seconds"] = -1
        C.write_json(path, meta)
        with self.assertRaisesRegex(ValueError, "invalid elapsed time"):
            verify_results.verify(self.out, C.DATA, C.DATA/"paper")

    def test_report_narrative_uses_generated_values(self):
        zero = C.read_csv(self.out/"zero_policy_comparison.csv")
        bins = C.read_csv(self.out/"binning_comparison.csv")
        target = next(r for r in zero if r["panel"] == "c_trigger_scenario" and r["pair"] == "android-harmony")
        target["all_rho"], target["drop_rho"] = "0.712345", "0.312345"
        target["all_strength"], target["drop_strength"] = "strong", "weak_or_none"
        plot_results.reports(self.out, zero, bins)
        plot_results.zero_chart(zero, self.out/"figures/zero_policy.svg")
        report = (self.out/"REPORT.md").read_text(encoding="utf-8")
        chart = (self.out/"figures/zero_policy.svg").read_text(encoding="utf-8")
        self.assertIn("0.712345 (strong) to 0.312345", report)
        self.assertIn("0.712 to 0.312", chart)
        self.assertNotIn("0.612637", report)


if __name__ == "__main__":
    unittest.main()
