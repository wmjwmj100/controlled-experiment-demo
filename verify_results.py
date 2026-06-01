#!/usr/bin/env python3
import csv

def verify():
    with open("results.csv") as f:
        rows = list(csv.DictReader(f))
        last = rows[-1]
        ctrl = float(last["control_height_cm"])
        treat = float(last["treatment_height_cm"])
        assert abs(ctrl - 12.57) < 0.1, f"control mismatch {ctrl}"
        assert abs(treat -14.96) <0.1, f"treatment mismatch {treat}"
        print("ok")
verify()