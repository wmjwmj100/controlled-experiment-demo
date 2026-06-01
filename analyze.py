#!/usr/bin/env python3
"""analyze.py - Dui zhao shi yan jie guo cha yi fen xi gong ju."""

import argparse
import csv
import math
import sys


def read_wide_csv(path):
    control, treatment = [], []
    days = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            days.append(int(row["day"]))
            for ckey in ["control_height", "control_height_cm"]:
                if ckey in row and row[ckey].strip():
                    control.append(float(row[ckey]))
                    break
            for ekey in ["treatment_height", "treatment_height_cm"]:
                if ekey in row and row[ekey].strip():
                    treatment.append(float(row[ekey]))
                    break
    return days, control, treatment


def read_long_csv(path):
    groups = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gname = row.get("\u7ec4\u540d", "").strip()
            try:
                day = int(row.get("\u5929\u6570", 0))
                value = float(row.get("\u89c2\u6d4b\u503c", 0))
            except (ValueError, TypeError):
                continue
            if gname not in groups:
                groups[gname] = []
            groups[gname].append((day, value))
    for g in groups:
        groups[g].sort(key=lambda x: x[0])
    names = list(groups.keys())
    if len(names) >= 2:
        return groups[names[0]], groups[names[1]], names[0], names[1]
    return None, None, None, None


def compute_stats(values):
    n = len(values)
    if n == 0:
        return {"n": 0}
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / n if n > 1 else 0
    std = math.sqrt(variance)
    return {"n": n, "mean": mean, "std": std}


def analyze(days, ctrl, treat, path):
    sep = "=" * 60
    print()
    print(sep)
    print("  Shi yan jie guo cha yi fen xi bao gao")
    print(f"  Shu ju lai yuan: {path}")
    print(sep)
    n = len(ctrl)
    if n < 2:
        print("  [cuo wu] shu ju dian bu zu")
        return
    td = days[-1] if days else n - 1
    fc, ft = ctrl[-1], treat[-1]
    ad = ft - fc
    rp = (ad / fc * 100) if fc != 0 else 0
    gc, gt = ctrl[-1] - ctrl[0], treat[-1] - treat[0]
    dc, dt = gc / td if td > 0 else 0, gt / td if td > 0 else 0
    cd = [ctrl[i] - ctrl[i-1] for i in range(1, n)]
    tdd = [treat[i] - treat[i-1] for i in range(1, n)]
    cs = compute_stats(cd)
    ts = compute_stats(tdd)
    print(f"  [1] Zhong dian dui bi")
    print(f"      Dui zhao: {fc:.3f}, Shi yan: {ft:.3f}")
    print(f"      Cha yi: {ad:+.3f} ({rp:+.1f}%)")
    print(f"  [2] Zeng zhang dui bi")
    print(f"      Dui zhao zeng zhang: {gc:.3f} (ri jun {dc:.3f})")
    print(f"      Shi yan zeng zhang: {gt:.3f} (ri jun {dt:.3f})")
    print(f"  [3] Bo dong fen xi")
    print(f"      Dui zhao ri jun: mean={cs['mean']:.3f}, std={cs['std']:.3f}")
    print(f"      Shi yan ri jun: mean={ts['mean']:.3f}, std={ts['std']:.3f}")
    if cs['std'] > 0 and ts['std'] > 0:
        r = ts['std'] / cs['std']
        print(f"      Bo dong bi: {r:.2f}")
        if r > 1.5:
            print("      [!] Shi yan zu bo dong ming xian")
        elif r < 0.5:
            print("      [!] Dui zhao zu bo dong ming xian")
    print(f"  [4] Chu bu zhen duan")
    if ad > 0 and rp > 10:
        print(f"      [+] Liang zu cha yi ming xian (> {abs(rp):.0f}%)")
    elif ad > 0 and rp > 5:
        print("      [~] Qing wei cha yi, jian yi zeng jia yang ben")
    else:
        print("      [~] Cha yi hen xiao, ke neng wu shi ji yi yi")
    if cs['std'] > dc * 0.5 or ts['std'] > dt * 0.5:
        print("      [!] Shu ju zao shen jiao da")
    print()
    print(sep)
    print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--csv", required=True)
    parser.add_argument("--format", choices=["auto", "wide", "long"], default="auto")
    args = parser.parse_args()
    fmt = args.format
    if fmt == "auto":
        with open(args.csv, newline="", encoding="utf-8") as f:
            h = f.readline().strip().lower()
        fmt = "long" if "\u7ec4\u540d" in h else "wide"
    if fmt == "wide":
        days, ctrl, treat = read_wide_csv(args.csv)
        if not ctrl:
            print("can not identify columns")
            sys.exit(1)
        analyze(days, ctrl, treat, args.csv)
    else:
        g1, g2, n1, n2 = read_long_csv(args.csv)
        if g1 is None:
            print("can not identify groups")
            sys.exit(1)
        print(f"Groups: [{n1}] vs [{n2}]")
        analyze([d for d,_ in g1], [v for _,v in g1], [v for _,v in g2], args.csv)


if __name__ == "__main__":
    main()
