#!/usr/bin/env python3
"""Analyze controlled experiment results — with diagnostic checks.

Reads experiment CSV output (wide or long format), computes per-group
statistics, treatment-vs-control comparison, data quality checks,
divergence classification, and generates a readable diagnostic report.

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


def extract_timeseries(rows):
    """Extract per-column timeseries from wide-format data.

    Returns dict {col_name: [(day_index, value), ...]} sorted by day.
    Only works if there's a 'day' (or 'Day'/'days') column.
    """
    if not rows:
        return {}
    headers = list(rows[0].keys())
    day_col = None
    for candidate in ("day", "Day", "days"):
        if candidate in headers:
            day_col = candidate
            break
    if day_col is None:
        return {}

    series = {}
    for h in headers:
        if h == day_col:
            continue
        pairs = []
        for r in rows:
            if isinstance(r.get(day_col), (int, float)) and isinstance(r.get(h), (int, float)):
                pairs.append((int(r[day_col]), r[h]))
        pairs.sort(key=lambda x: x[0])
        if pairs:
            series[h] = pairs
    return series


def is_monotonic_increasing(values):
    """Check if a sequence is non-decreasing (within tolerance).
    Returns list of (index, prev_val, curr_val, drop_amount).
    """
    drops = []
    for i in range(1, len(values)):
        if values[i] < values[i-1] - 1e-9:
            drops.append((i, values[i-1], values[i], values[i-1] - values[i]))
    return drops


def detect_abnormal_jumps(values, z_threshold=3.0):
    """Detect day-over-day changes that exceed z_threshold * std of changes.

    Returns list of (index, change, severity) tuples.
    """
    if len(values) < 3:
        return []
    deltas = [values[i] - values[i-1] for i in range(1, len(values))]
    if len(deltas) < 2:
        return []
    mean_delta = sum(deltas) / len(deltas)
    var_delta = sum((d - mean_delta)**2 for d in deltas) / (len(deltas) - 1)
    std_delta = math.sqrt(var_delta) if var_delta > 0 else 0.001

    flags = []
    for i, d in enumerate(deltas):
        if abs(d - mean_delta) > z_threshold * std_delta:
            severity = "major" if abs(d - mean_delta) > 4 * std_delta else "minor"
            flags.append((i + 1, d, severity))
    return flags


def check_start_values(series_dict):
    """Check if all groups start from the same point.
    Returns list of (ref_name, other_name, ref_val, other_val, pct_diff).
    """
    starts = {}
    for name, pairs in series_dict.items():
        if pairs:
            starts[name] = pairs[0][1]
    if len(starts) < 2:
        return []
    issues = []
    ref_name = list(starts.keys())[0]
    ref_val = starts[ref_name]
    for name, val in starts.items():
        if name == ref_name:
            continue
        if abs(val - ref_val) > 1e-6:
            pct = ((val - ref_val) / ref_val * 100) if ref_val != 0 else 0
            issues.append((ref_name, name, ref_val, val, pct))
    return issues


def check_missing_values(rows, headers):
    """Check for missing or non-numeric values in numeric columns.
    Returns list of (row_index, column_name, issue_type).
    """
    issues = []
    for i, row in enumerate(rows):
        for h in headers:
            v = row.get(h)
            if v is None or (isinstance(v, str) and v.strip() == ""):
                issues.append((i, h, "missing"))
    return issues


def classify_divergence(stats_dict, series_dict):
    """Classify the nature of divergence between groups.

    Returns a dict with diagnostic info:
      - details: snr, signal_quality, variance_ratio, divergence_pattern, onset
      - flags: list of warning flags
    """
    result = {"flags": [], "details": {}}

    names = list(stats_dict.keys())
    if len(names) < 2:
        return result

    # Identify control vs treatment by name heuristics
    ctrl_idx = 0
    treat_idx = 1
    for i, n in enumerate(names):
        if "control" in n.lower() or "ctrl" in n.lower():
            ctrl_idx = i
        if "treatment" in n.lower() or "treat" in n.lower():
            treat_idx = i

    ctrl_name = names[ctrl_idx]
    treat_name = names[treat_idx]
    ctrl = stats_dict[ctrl_name]
    treat = stats_dict[treat_name]

    # 1. Signal-to-noise ratio
    effect = treat["last"] - ctrl["last"]
    pooled_std = math.sqrt((ctrl["std"]**2 + treat["std"]**2) / 2) if ctrl["std"] + treat["std"] > 0 else 0.001
    snr = abs(effect) / pooled_std if pooled_std > 0 else 0
    result["details"]["snr"] = round(snr, 2)
    if snr > 3.0:
        result["details"]["signal_quality"] = "high"
    elif snr > 1.5:
        result["details"]["signal_quality"] = "moderate"
    else:
        result["details"]["signal_quality"] = "low"
        result["flags"].append("weak_signal")

    # 2. Variance ratio
    vr = treat["std"] / ctrl["std"] if ctrl["std"] > 0 else 99
    result["details"]["variance_ratio"] = round(vr, 2)
    if vr > 2.0:
        result["flags"].append("treatment_variance_much_higher")
    elif vr > 1.5:
        result["flags"].append("treatment_variance_higher")

    # 3. Divergence onset analysis
    if ctrl_name in series_dict and treat_name in series_dict:
        ctrl_pairs = dict(series_dict[ctrl_name])
        treat_pairs = dict(series_dict[treat_name])
        common_days = sorted(set(ctrl_pairs.keys()) & set(treat_pairs.keys()))

        if len(common_days) >= 3:
            half_span = len(common_days) // 2
            first_half_diffs = []
            second_half_diffs = []
            for d in common_days:
                diff = treat_pairs[d] - ctrl_pairs[d]
                if d <= common_days[half_span]:
                    first_half_diffs.append(diff)
                else:
                    second_half_diffs.append(diff)

            early_avg = sum(first_half_diffs) / len(first_half_diffs) if first_half_diffs else 0
            late_avg = sum(second_half_diffs) / len(second_half_diffs) if second_half_diffs else 0

            if abs(late_avg) > abs(early_avg) * 1.5 and abs(early_avg) > 0.01:
                result["details"]["divergence_pattern"] = "progressive"
                result["details"]["onset"] = "early_and_widening"
            elif abs(late_avg) > abs(early_avg) * 1.5:
                result["details"]["divergence_pattern"] = "late"
                result["details"]["onset"] = "late_separation"
                result["flags"].append("late_divergence")
            elif abs(early_avg) > 0.1 and abs(late_avg - early_avg) < 0.5 * max(abs(early_avg), 0.01):
                result["details"]["divergence_pattern"] = "constant_offset"
                result["details"]["onset"] = "consistent_offset"
            else:
                result["details"]["divergence_pattern"] = "irregular"
                result["flags"].append("irregular_divergence")

        # Late acceleration check
        if len(common_days) >= 5:
            last_third = common_days[-len(common_days)//3:]
            earlier = common_days[:len(common_days)//3]
            late_diffs = [treat_pairs[d] - ctrl_pairs[d] for d in last_third]
            early_diffs = [treat_pairs[d] - ctrl_pairs[d] for d in earlier]
            if late_diffs and early_diffs:
                late_mean = sum(late_diffs) / len(late_diffs)
                early_mean = sum(early_diffs) / len(early_diffs)
                if abs(late_mean) > 2 * abs(early_mean) and abs(early_mean) > 0.1:
                    result["flags"].append("late_acceleration")

    # 4. Growth rate stability
    if ctrl_name in series_dict:
        ctrl_vals = [v for _, v in series_dict[ctrl_name]]
    else:
        ctrl_vals = []
    if treat_name in series_dict:
        treat_vals = [v for _, v in series_dict[treat_name]]
    else:
        treat_vals = []

    if len(ctrl_vals) >= 3:
        ctrl_deltas = [ctrl_vals[i] - ctrl_vals[i-1] for i in range(1, len(ctrl_vals))]
        ctrl_delta_mean = sum(ctrl_deltas) / len(ctrl_deltas)
        ctrl_delta_var = sum((d - ctrl_delta_mean)**2 for d in ctrl_deltas) / (len(ctrl_deltas)-1) if len(ctrl_deltas) > 1 else 0
        ctrl_delta_std = math.sqrt(ctrl_delta_var) if ctrl_delta_var > 0 else 0
    else:
        ctrl_delta_std = 0

    if len(treat_vals) >= 3:
        treat_deltas = [treat_vals[i] - treat_vals[i-1] for i in range(1, len(treat_vals))]
        treat_delta_mean = sum(treat_deltas) / len(treat_deltas)
        treat_delta_var = sum((d - treat_delta_mean)**2 for d in treat_deltas) / (len(treat_deltas)-1) if len(treat_deltas) > 1 else 0
        treat_delta_std = math.sqrt(treat_delta_var) if treat_delta_var > 0 else 0
    else:
        treat_delta_std = 0

    result["details"]["ctrl_daily_std"] = round(ctrl_delta_std, 3)
    result["details"]["treat_daily_std"] = round(treat_delta_std, 3)

    if treat_delta_std > 2 * ctrl_delta_std and ctrl_delta_std > 0.01:
        result["flags"].append("treatment_growth_unstable")

    return result


def analyze_csv(path):
    """Analyze experiment CSV and return structured results.

    Returns a dict with keys: path, row_count, groups, comparison, quality, divergence
    """
    headers, rows = load_csv(path)
    groups = find_groups(rows)
    series = extract_timeseries(rows)

    result = {
        "path": str(path),
        "row_count": len(rows),
        "groups": {},
        "comparison": None,
        "quality": {},
        "divergence": {},
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

    # --- Data quality checks ---
    quality = {
        "missing_values": [],
        "monotonicity_issues": {},
        "abnormal_jumps": {},
        "start_value_issues": [],
    }

    quality["missing_values"] = check_missing_values(rows, headers)

    for name, pairs in series.items():
        vals = [v for _, v in pairs]
        drops = is_monotonic_increasing(vals)
        if drops:
            quality["monotonicity_issues"][name] = [
                {"day": d[0], "prev": round(d[1], 3), "curr": round(d[2], 3), "drop": round(d[3], 3)}
                for d in drops
            ]
        jumps = detect_abnormal_jumps(vals)
        if jumps:
            quality["abnormal_jumps"][name] = [
                {"day": j[0], "change": round(j[1], 3), "severity": j[2]}
                for j in jumps
            ]

    quality["start_value_issues"] = check_start_values(series)
    result["quality"] = quality

    # --- Divergence classification ---
    if len(group_names) >= 2:
        result["divergence"] = classify_divergence(result["groups"], series)

    return result


def format_quality_report(quality):
    """Format quality check results. Returns (lines, has_issues)."""
    lines = []
    flagged = False

    if quality["missing_values"]:
        flagged = True
        lines.append(f"  [!] Missing values: {len(quality['missing_values'])} cell(s)")
        for row_idx, col, _ in quality["missing_values"][:5]:
            lines.append(f"      Row {row_idx}, column '{col}'")

    mono_issues = quality.get("monotonicity_issues", {})
    if mono_issues:
        flagged = True
        for name, drops in mono_issues.items():
            for d in drops[:3]:
                lines.append(f"  [!] {name}: Day {d['day']} dropped {d['drop']} (possible measurement error)")

    jumps = quality.get("abnormal_jumps", {})
    if jumps:
        flagged = True
        for name, jlist in jumps.items():
            for j in jlist:
                tag = "!!" if j["severity"] == "major" else "!"
                lines.append(f"  [{tag}] {name}: Day {j['day']} abnormal change {j['change']:+.3f} ({j['severity']})")

    if quality["start_value_issues"]:
        flagged = True
        for ref, name, ref_v, v, pct in quality["start_value_issues"]:
            lines.append(f"  [!] Starting values differ: {name} ({v}) vs {ref} ({ref_v}), diff {pct:+.1f}%")

    if not flagged:
        lines.append("  No data quality issues detected.")

    return lines, flagged


def format_divergence_report(divergence):
    """Format divergence classification results."""
    lines = []
    if not divergence or not divergence.get("details"):
        return lines

    d = divergence["details"]
    flags = divergence.get("flags", [])

    sq = d.get("signal_quality", "unclear")
    snr = d.get("snr", "?")
    lines.append(f"  Signal-to-noise ratio: {snr} ({sq})")

    vr = d.get("variance_ratio", "?")
    lines.append(f"  Variance ratio (treatment/control): {vr}")

    pattern = d.get("divergence_pattern", "insufficient data")
    if pattern == "progressive":
        lines.append(f"  Pattern: Divergence appears early and widens over time")
        lines.append(f"  -> Likely a genuine treatment effect, growing with exposure")
    elif pattern == "constant_offset":
        lines.append(f"  Pattern: Constant offset between groups throughout")
        lines.append(f"  -> Possible initial condition difference, check randomization")
    elif pattern == "late":
        lines.append(f"  Pattern: Groups track together initially, diverge later")
        lines.append(f"  -> Could indicate late-acting variable or cumulative effect")
    elif pattern == "irregular":
        lines.append(f"  Pattern: Irregular, no clear divergence trend")
        lines.append(f"  -> High noise relative to effect; may need more data")

    flag_meanings = {
        "weak_signal": "  [!] Effect size is small relative to noise \u2014 results may not be reproducible",
        "treatment_variance_much_higher": "  [!] Treatment group variance is much higher than control \u2014 possible uncontrolled variable",
        "treatment_variance_higher": "  [!] Treatment group variance moderately higher \u2014 check for outliers",
        "late_divergence": "  [!] Divergence appears late \u2014 check if something changed mid-experiment",
        "late_acceleration": "  [!] Treatment group accelerated in later phase \u2014 possible cumulative or threshold effect",
        "irregular_divergence": "  [!] No clear divergence pattern \u2014 consider longer observation or reduced noise",
        "treatment_growth_unstable": "  [!] Treatment group daily growth is erratic \u2014 could indicate measurement issue or environmental factor",
    }
    for f in flags:
        if f in flag_meanings:
            lines.append(flag_meanings[f])

    return lines


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

    # Data quality section
    lines.append("-" * 55)
    lines.append("  Data Quality Checks")
    lines.append("-" * 55)
    q_lines, _ = format_quality_report(result["quality"])
    lines.extend(q_lines)
    lines.append("")

    # Divergence diagnosis section
    if result["divergence"] and result["divergence"].get("details"):
        lines.append("-" * 55)
        lines.append("  Divergence Diagnosis")
        lines.append("-" * 55)
        d_lines = format_divergence_report(result["divergence"])
        lines.extend(d_lines)
        lines.append("")

    # Troubleshooting guide
    lines.append("-" * 55)
    lines.append("  Troubleshooting Guide")
    lines.append("-" * 55)
    lines.append("  If results don't match expectations, check in this order:")
    lines.append("    1. Data quality: Are there anomalies in the raw measurements?")
    lines.append("    2. Divergence pattern: Does the difference look real or random?")
    lines.append("    3. Design: Could an uncontrolled variable explain the pattern?")
    lines.append("    4. Reproduce: Run with a different seed to check stability")
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
