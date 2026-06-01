#!/usr/bin/env python3
"""Plot experiment results from simulate_experiment.py output CSV."""

import argparse
import csv
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


def plot_results(csv_path, output_path=None):
    csv_path = Path(csv_path)
    days, ctrl, treat = [], [], []
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            days.append(int(row['day']))
            ctrl.append(float(row['control_height_cm']))
            treat.append(float(row['treatment_height_cm']))

    if not HAS_MPL:
        print(f"Results from {csv_path}")
        print(f"{'Day':>4}  {'Control':>8}  {'Treatment':>10}")
        print('-' * 28)
        for d, c, t in zip(days, ctrl, treat):
            print(f"{d:4d}  {c:8.2f}  {t:10.2f}")
        print(f"Control final: {ctrl[-1]:.2f} cm")
        print(f"Treatment final: {treat[-1]:.2f} cm")
        print(f"Difference: {treat[-1] - ctrl[-1]:.2f} cm")
        return

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(days, ctrl, 'o-', label='Control (every 2 days)', color='#4c72b0')
    ax.plot(days, treat, 's-', label='Treatment (every day)', color='#dd8452')
    ax.set_xlabel('Day')
    ax.set_ylabel('Height (cm)')
    ax.set_title('Plant Growth: Control vs Treatment')
    ax.legend()
    ax.grid(True, alpha=0.3)

    out = Path(output_path) if output_path else csv_path.with_suffix('.png')
    fig.savefig(out, dpi=150, bbox_inches='tight')
    print(f"Plot saved to {out}")
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('csv', help='Path to results.csv')
    parser.add_argument('--output', '-o', help='Output image path')
    args = parser.parse_args()
    plot_results(args.csv, args.output)
