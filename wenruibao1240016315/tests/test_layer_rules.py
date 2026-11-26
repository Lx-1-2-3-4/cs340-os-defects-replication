"""Tests for the layer-composition analysis.

Run from this folder:
    python -m unittest discover -s tests -v

The tests cover the pieces that are easy to get wrong silently: the distance
metric, the support rule, the composition percentages, and the consistency of
the "explained" column with the raw and standardised distances.
"""

from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import common as C  # noqa: E402
import layer_analysis as LA  # noqa: E402


def read_csv(name):
    with open(ROOT / "results" / name, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class TestDistance(unittest.TestCase):
    def test_identical_distributions(self):
        self.assertAlmostEqual(LA.jsd([3, 1, 4], [30, 10, 40]), 0.0, places=12)

    def test_disjoint_distributions(self):
        self.assertAlmostEqual(LA.jsd([1, 0, 0], [0, 0, 1]), 1.0, places=12)

    def test_symmetry(self):
        a, b = [5, 3, 1, 1], [1, 2, 8, 4]
        self.assertAlmostEqual(LA.jsd(a, b), LA.jsd(b, a), places=12)

    def test_zero_vector_rejected(self):
        with self.assertRaises(ValueError):
            LA.as_distribution([0, 0, 0])


class TestComposition(unittest.TestCase):
    def setUp(self):
        self.rows = read_csv("layer_composition.csv")

    def test_every_system_has_500_defects(self):
        by_system = {}
        for row in self.rows:
            by_system[row["system"]] = by_system.get(row["system"], 0) + int(row["defects"])
        self.assertEqual(by_system, {"android": 500, "linux": 500, "harmony": 500})

    def test_shares_sum_to_100(self):
        for system in C.SYSTEMS:
            total = sum(float(r["share_pct"]) for r in self.rows if r["system"] == system)
            self.assertAlmostEqual(total, 100.0, delta=0.05)

    def test_runtimevm_excluded(self):
        runtime = [r for r in self.rows if r["layer"] == "RuntimeVM"]
        self.assertTrue(runtime)
        for row in runtime:
            self.assertEqual(row["common_support"], "no")

    def test_five_common_layers(self):
        common = {r["layer"] for r in self.rows if r["common_support"] == "yes"}
        self.assertEqual(common, {"Kernel", "SystemLib", "Framework",
                                  "SystemService", "Application"})


class TestDistances(unittest.TestCase):
    def setUp(self):
        self.rows = read_csv("layer_distances.csv")

    def test_six_rows(self):
        self.assertEqual(len(self.rows), 6)
        self.assertEqual({r["dimension"] for r in self.rows}, {"function", "trigger"})
        self.assertEqual(len({r["pair"] for r in self.rows}), 3)

    def test_explained_column_consistent(self):
        for row in self.rows:
            raw = float(row["jsd_raw"])
            pooled = float(row["jsd_standardised_pooled"])
            expected = round(100.0 * (raw - pooled) / raw, 1)
            self.assertAlmostEqual(float(row["explained_by_composition_pct"]),
                                   expected, delta=0.05)

    def test_values_are_probability_distances(self):
        for row in self.rows:
            for column in ("jsd_raw", "jsd_standardised_pooled",
                           "jsd_standardised_uniform", "jsd_within_layer"):
                value = float(row[column])
                self.assertGreaterEqual(value, 0.0)
                self.assertLessEqual(value, 1.0)


class TestAgainstDataset(unittest.TestCase):
    def test_composition_matches_dataset(self):
        data = C.load_dataset()
        for system in C.SYSTEMS:
            counts = {}
            for row in data[system]:
                layer = C.LAYER[row["OS Layer"]]
                counts[layer] = counts.get(layer, 0) + 1
            rows = {r["layer"]: int(r["defects"]) for r in read_csv("layer_composition.csv")
                    if r["system"] == system}
            self.assertEqual(rows, {layer: counts.get(layer, 0)
                                    for layer in C.CATEGORY_ORDER["os_layer"]})


if __name__ == "__main__":
    unittest.main()
