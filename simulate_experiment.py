#!/usr/bin/env python3
"""Minimal verifiable controlled experiment demo.

Simulates plant growth under two different watering frequencies,
with controlled single variable and reproducible random seed.
"""

import argparse
import csv
import random
from pathlib import Path


def simulate_growth(days, initial_height, daily_gain_mean, noise_std, seed):
    random.seed(seed)
    heights = [initial_height]
    for _ in range(days - 1):
        gain = random.gauss(daily_gain_mean, noise_std)
        heights.append(max(0.0, heights[-1] + gain))
    return heights


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=14, help='Total observation days')
    parser.add_argument('--output', default='results.csv', help='Output CSV path')
    parser.add_argument('--seed', type=int, default=42, help='Fixed random seed for reproducibility')
    args = parser.parse_args(argv)

    days = args.days
    day_range = list(range(days))

    # Control group: water every 2 days, moderate stable growth
    ctrl_heights = simulate_growth(
        days,
        initial_height=2.0,
        daily_gain_mean=0.8,
        noise_std=0.25,
        seed=args.seed,
    )

    # Treatment group: water every day, slightly faster initial growth + small extra noise
    treatment_heights = simulate_growth(
        days,
        initial_height=2.0,
        daily_gain_mean=1.0,
        noise_std=0.35,
        seed=args.seed + 1,
    )

    out_path = Path(args.output)
    with out_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['day', 'control_height_cm', 'treatment_height_cm'])
        for day, ctrl, treat in zip(day_range, ctrl_heights, treatment_heights):
            writer.writerow([day, round(ctrl, 3), round(treat, 3)])

    print(f'Experiment simulation complete. Results written to {out_path.resolve()}')
    final_ctrl = ctrl_heights[-1]
    final_treat = treatment_heights[-1]
    print(f'Final height control  (every 2 days): {final_ctrl:.2f} cm')
    print(f'Final height treatment (every day):  {final_treat:.2f} cm')


if __name__ == '__main__':
    main()
