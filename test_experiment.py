#!/usr/bin/env python3
"""Tests for the controlled experiment demo.

Run:  python3 test_experiment.py
"""

import csv
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure we can import project modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import simulate_experiment
from experiment import Experiment


class TestSimulation(unittest.TestCase):
    """Test the core simulation logic."""

    def test_default_seed_reproducibility(self):
        """Same seed must produce identical results."""
        h1 = simulate_experiment.simulate_growth(14, 2.0, 0.8, 0.25, 42)
        h2 = simulate_experiment.simulate_growth(14, 2.0, 0.8, 0.25, 42)
        self.assertEqual(h1, h2)

    def test_different_seed_different_results(self):
        """Different seeds should (almost certainly) produce different results."""
        h1 = simulate_experiment.simulate_growth(14, 2.0, 0.8, 0.25, 42)
        h2 = simulate_experiment.simulate_growth(14, 2.0, 0.8, 0.25, 99)
        self.assertNotEqual(h1, h2)

    def test_growth_increases_over_time(self):
        """Plant height should generally increase."""
        heights = simulate_experiment.simulate_growth(14, 2.0, 0.8, 0.25, 42)
        self.assertGreater(heights[-1], heights[0])

    def test_initial_height(self):
        """First height must match initial_height."""
        heights = simulate_experiment.simulate_growth(14, 2.0, 0.8, 0.25, 42)
        self.assertEqual(heights[0], 2.0)

    def test_no_negative_heights(self):
        """Height should never go below zero."""
        heights = simulate_experiment.simulate_growth(14, 2.0, 0.8, 0.25, 42)
        self.assertTrue(all(h >= 0 for h in heights))


class TestCSVOutput(unittest.TestCase):
    """Test CSV generation from simulation."""

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w")
        self.tmp.close()

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_csv_columns_and_length(self):
        """CSV should have correct columns and 14 data rows."""
        simulate_experiment.main(["--days", "14", "--output", self.tmp.name, "--seed", "42"])
        with open(self.tmp.name, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertEqual(len(rows), 14)
        self.assertIn("day", rows[0])
        self.assertIn("control_height_cm", rows[0])
        self.assertIn("treatment_height_cm", rows[0])

    def test_csv_with_custom_params(self):
        """Custom days and seed should produce expected row count."""
        simulate_experiment.main(["--days", "30", "--output", self.tmp.name, "--seed", "123"])
        with open(self.tmp.name, newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 30)


class TestExperimentClass(unittest.TestCase):
    """Test the Experiment data recording class."""

    def test_add_group(self):
        exp = Experiment("test")
        self.assertTrue(exp.add_group("A", "condition x"))
        self.assertFalse(exp.add_group("A", "duplicate"))  # duplicate

    def test_record_and_summary(self):
        exp = Experiment("test")
        exp.add_group("Ctrl", "standard")
        exp.add_group("Exp", "treatment")
        exp.record("Ctrl", 1, 2.0)
        exp.record("Ctrl", 7, 5.0)
        exp.record("Exp", 1, 2.0)
        exp.record("Exp", 7, 7.0)
        summary = exp.summary()
        self.assertIn("Ctrl", summary)
        self.assertIn("Exp", summary)

    def test_record_to_nonexistent_group(self):
        exp = Experiment("test")
        result = exp.record("Ghost", 1, 1.0)
        self.assertFalse(result)

    def test_export_csv(self):
        exp = Experiment("test")
        exp.add_group("Ctrl", "standard")
        exp.record("Ctrl", 1, 2.0)
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            tmpname = f.name
        try:
            exp.export_csv(tmpname)
            with open(tmpname, newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertGreater(len(rows), 0)
        finally:
            os.unlink(tmpname)


if __name__ == "__main__":
    unittest.main()
