#!/usr/bin/env python3
"""Analyze controlled experiment results.

Reads experiment CSV output (wide or long format), computes per-group
statistics, treatment-vs-control comparison, and generates a readable
summary report.

Usage:
  python3 analyze.py results.csv

As a library:
  from analyze import analyze_csv
  stats = analyze_csv("results.csv")
"""

import csv
import math
import sys
from pathlib import Path


def load_csv(path):
    """Return (headers, rows) where rows is a list of dicts."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        if not headers:
            print(f"Error: {path} is empty or has no header", file=sys.stderr)
            sys.exit(1)
        rows = []
        for row in reader:
            cleaned = {}
            for k, v in row.items():
                try:
                    cleaned[k] = float(v)
                except (ValueError, TypeError):
                    cleaned[k] = v
            rows.append(cleaned)
        return headers, rows


def numeric_columns(headers, rows):
    """Return list of column names that contain all numeric values."""
    return [h for h in headers
            if all(isinstance(r.get(h), (int, float)) for r in rows)]


def column_stats(values):
    """Compute basic statistics for a list of numbers."""
    n = len(values)
    if n == 0:
        return None
    total = sum(values)
    mean = total / n
    variance = sum((x - mean) ** 2 for x in values) / (n - 1) if n > 1 else 0.0
    std = math.sqrt(variance)
    return {
        "count": n,
        "mean": mean,
        "std": std,
        "min": min(values),
        "max": max(values),
        "first": values[0],
        "last": values[-1],
        "change": values[-1] - values[0],
    }


def find_groups(rows):
    """Detect if data is in wide or long format and extract groups.

    Wide format: each column is a group (e.g. control_height_cm, treatment_height_cm)
    Long format: has 'group' and 'value' columns
    Returns a dict of {group_name: [values]}.
    """
    if not rows:
        return {}
    headers = list(rows[0].keys())
    # Check for long format
    if "group" in headers and "value" in headers:
        groups = {}
        for r in rows:
            g = str(r["group"])
            v = r["value"] if isinstance(r.get("value"), (int, float)) else 0
            groups.setdefault(g, []).append(v)
        return groups
    # Check for wide format with control/treatment columns
    if "control_height_cm" in headers or "control" in headers:
        groups = {}
        for h in headers:
            if h in ("day", "Day", "days"):
                continue
            vals = [r[h] for r in rows if isinstance(r.get(h), (int, float))]
            if vals:
                label = h.replace("_height_cm", "").replace("_", " ").title()
                groups[label] = vals
        return groups
    # Generic: treat each numeric column as a group
    num_cols = numeric_columns(headers, rows)
    groups = {}
    for h in num_cols:
        vals = [r[h] for r in rows if isinstance(r.get(h), (int, float))]
        if vals:
            groups[h] = vals
    return groups


def analyze_csv(path):
    """Analyze experiment CSV and return structured results.

    Returns a dict with keys: path, row_count, groups, comparison
    """
    headers, rows = load_csv(path)
    groups = find_groups(rows)
    result = {
        "path": str(path),
        "row_count": len(rows),
        "groups": {},
        "comparison": None,
    }
    for name, values in groups.items():
        stats = column_stats(values)
        if stats:
            result["groups"][name] = stats

    # Compare groups if there are at least two
    group_names = list(result["groups"].keys())
    if len(group_names) >= 2:
        base = group_names[0]
        comparisons = []
        for other in group_names[1:]:
            base_last = result["groups"][base]["last"]
            other_last = result["groups"][other]["last"]
            diff = other_last - base_last
            pct = (diff / base_last * 100) if base_last != 0 else 0
            comparisons.append({
                "control": base,
                "treatment": other,
                "control_final": round(base_last, 3),
                "treatment_final": round(other_last, 3),
                "absolute_diff": round(diff, 3),
                "percent_diff": round(pct, 2),
                "treatment_higher": other_last > base_last,
            })
        result["comparison"] = comparisons
    return result


def format_report(result):
    """Format analysis results as a human-readable string."""
    lines = []
    lines.append("=" * 55)
    lines.append(f"Experiment Analysis: {Path(result['path']).name}")
    lines.append("=" * 55)
    lines.append(f"Data points: {result['row_count']} rows")
    lines.append("")

    for name, stats in result["groups"].items():
        lines.append(f"  {name}:")
        lines.append(f"    Initial:  {stats['first']:.3f}")
        lines.append(f"    Final:    {stats['last']:.3f}")
        lines.append(f"    Change:   {stats['change']:+.3f}")
        lines.append(f"    Mean:     {stats['mean']:.3f}  (SD: {stats['std']:.3f})")
        lines.append(f"    Range:    [{stats['min']:.3f}, {stats['max']:.3f}]")
        lines.append("")

    if result["comparison"]:
        lines.append("-" * 55)
        for comp in result["comparison"]:
            lines.append(f"  {comp['treatment']} vs {comp['control']}:")
            lines.append(f"    Final:   {comp['treatment_final']} vs {comp['control_final']}")
            lines.append(f"    Diff:    {comp['absolute_diff']:+.3f}  ({comp['percent_diff']:+.2f}%)")
            if comp['treatment_higher']:
                lines.append(f"    Verdict: Treatment group grew more than control")
            else:
                lines.append(f"    Verdict: No positive treatment effect detected")
            lines.append("")

    lines.append("=" * 55)
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python3 {Path(sys.argv[0]).name} <experiment.csv>")
        print(f"       python3 {Path(sys.argv[0]).name} results.csv")
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"Error: {csv_path} not found", file=sys.stderr)
        sys.exit(1)

    result = analyze_csv(csv_path)
    print(format_report(result))


if __name__ == "__main__":
    main()
