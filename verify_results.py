#!/usr/bin/env python3
import csv

def generate_group_comparison(csv_path="results.csv"):
    """Generate standardized group comparison structure as per interface contract."""
    with open(csv_path) as f:
        rows = list(csv.DictReader(f))
        # Extract control and treatment values
        control_values = [float(row["control_height_cm"]) for row in rows]
        treatment_values = [float(row["treatment_height_cm"]) for row in rows]
        # Extract timeseries (day as index, 0-based)
        timeseries = {
            "Control": [(i, val) for i, val in enumerate(control_values)],
            "Treatment": [(i, val) for i, val in enumerate(treatment_values)]
        }
        # Verify final values as original check
        assert abs(control_values[-1] - 12.57) < 0.1, f"control mismatch {control_values[-1]}"
        assert abs(treatment_values[-1] -14.96) <0.1, f"treatment mismatch {treatment_values[-1]}"
        # Build the standardized structure
        return {
            "groups": {"Control": control_values, "Treatment": treatment_values},
            "timeseries": timeseries,
            "metadata": {"csv_path": csv_path, "row_count": len(rows)}
        }

if __name__ == "__main__":
    comparison = generate_group_comparison()
    print("Group comparison generated successfully")
