#!/usr/bin/env python3
"""Unit tests for the controlled experiment simulation.

Zero external dependencies — uses only Python standard library.
Run with:  python3 -m unittest test_simulate.py
"""

import csv
import os as os_mod
import tempfile
import unittest

from simulate_experiment import simulate_growth, main as sim_main


class TestSimulateGrowth(unittest.TestCase):
    """Tests for the core simulation function."""

    def test_returns_correct_length(self):
        heights = simulate_growth(days=10, initial_height=2.0,
                                  daily_gain_mean=0.8, noise_std=0.25, seed=42)
        self.assertEqual(len(heights), 10)

    def test_starts_at_initial_height(self):
        heights = simulate_growth(days=5, initial_height=3.0,
                                  daily_gain_mean=0.5, noise_std=0.1, seed=1)
        self.assertAlmostEqual(heights[0], 3.0)

    def test_reproducible_same_seed(self):
        h1 = simulate_growth(days=14, initial_height=2.0,
                             daily_gain_mean=0.8, noise_std=0.25, seed=42)
        h2 = simulate_growth(days=14, initial_height=2.0,
                             daily_gain_mean=0.8, noise_std=0.25, seed=42)
        self.assertEqual(h1, h2)

    def test_different_seed_different_results(self):
        h1 = simulate_growth(days=14, initial_height=2.0,
                             daily_gain_mean=0.8, noise_std=0.25, seed=42)
        h2 = simulate_growth(days=14, initial_height=2.0,
                             daily_gain_mean=0.8, noise_std=0.25, seed=99)
        self.assertNotEqual(h1, h2)

    def test_all_non_negative(self):
        heights = simulate_growth(days=100, initial_height=0.5,
                                  daily_gain_mean=-0.1, noise_std=0.5, seed=7)
        for h in heights:
            self.assertGreaterEqual(h, 0.0)

    def test_single_day(self):
        heights = simulate_growth(days=1, initial_height=5.0,
                                  daily_gain_mean=1.0, noise_std=0.0, seed=0)
        self.assertEqual(len(heights), 1)
        self.assertAlmostEqual(heights[0], 5.0)


class TestSimulateMain(unittest.TestCase):
    """Tests for the CLI entry point."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def _run(self, output_name, seed=42, days=14):
        out_path = os_mod.path.join(self.tmp, output_name)
        import sys
        old_argv = sys.argv
        sys.argv = ["simulate_experiment.py",
                    "--days", str(days),
                    "--output", out_path,
                    "--seed", str(seed)]
        try:
            sim_main()
        finally:
            sys.argv = old_argv
        return out_path

    def test_creates_csv(self):
        path = self._run("test_out.csv")
        self.assertTrue(os_mod.path.exists(path))

    def test_csv_has_expected_columns(self):
        path = self._run("test_cols.csv")
        with open(path, newline="") as f:
            reader = csv.reader(f)
            headers = next(reader)
        self.assertEqual(headers, ["day", "control_height_cm", "treatment_height_cm"])

    def test_csv_row_count(self):
        path = self._run("test_rows.csv", days=7)
        with open(path, newline="") as f:
            rows = list(csv.reader(f))
        self.assertEqual(len(rows), 8)

    def test_reproducible_output(self):
        path1 = self._run("r1.csv", seed=42, days=14)
        path2 = self._run("r2.csv", seed=42, days=14)
        with open(path1) as f1, open(path2) as f2:
            self.assertEqual(f1.read(), f2.read())

    def test_default_seed_expected_values(self):
        path = self._run("expected.csv", seed=42, days=14)
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))
        last = rows[-1]
        ctrl = float(last["control_height_cm"])
        treat = float(last["treatment_height_cm"])
        self.assertAlmostEqual(ctrl, 12.566, delta=0.01)
        self.assertAlmostEqual(treat, 14.955, delta=0.01)


if __name__ == "__main__":
    unittest.main()
