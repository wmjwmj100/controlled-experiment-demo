#!/usr/bin/env python3
"""experiment.py - Record and analyze real experiment observations.

Use this when you have real (non-simulated) observation data.
It provides group management, daily recording, summary reports,
and CSV export - zero external dependencies."""

import csv
from datetime import datetime


class Experiment:
    """A controlled experiment data recorder."""

    def __init__(self, name, description=''):
        self.name = name
        self.description = description
        self.created_at = datetime.now()
        self.groups = {}

    def add_group(self, name, condition):
        if name not in self.groups:
            self.groups[name] = []
            print(f"[group] added '{name}': {condition}")
            return True
        print(f"[warn] group '{name}' already exists")
        return False

    def record(self, group, day, value, note=''):
        if group not in self.groups:
            print(f"[error] group '{group}' does not exist, call add_group() first")
            return False
        rec = {'day': day, 'value': value, 'note': note,
               'ts': datetime.now().isoformat()}
        self.groups[group].append(rec)
        print(f"[record] day {day} | {group}: {value} {note}")
        return True

    def summary(self):
        NL = chr(10)
        lines = [f"Experiment: {self.name}"]
        if self.description:
            lines.append(f"Description: {self.description}")
        lines.append(f"Groups: {len(self.groups)}")
        lines.append('')
        for gname, records in self.groups.items():
            lines.append(f"--- {gname} ---")
            if not records:
                lines.append('  (no data)')
                continue
            vals = [r['value'] for r in records]
            days = [r['day'] for r in records]
            lines.append(f"  Records: {len(records)}")
            lines.append(f"  Days: {min(days)} - {max(days)}")
            lines.append(f"  Latest: {vals[-1]}")
            if len(vals) > 1:
                lines.append(f"  Change: {vals[-1] - vals[0]:+.2f}")
            lines.append('')
        return NL.join(lines)

    def export_csv(self, path):
        with open(path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['group', 'day', 'value', 'note', 'timestamp'])
            for gname, records in self.groups.items():
                for r in sorted(records, key=lambda x: x['day']):
                    w.writerow([gname, r['day'], r['value'], r['note'], r['ts']])
        print(f"Exported: {path}")


def demo():
    print('=' * 50)
    print('experiment.py - Experiment Data Recorder')
    print('=' * 50)
    exp = Experiment('Watering Frequency Trial', 'Recording real observations')
    exp.add_group('Control', 'Water every 2 days')
    exp.add_group('Treatment', 'Water every day')
    exp.record('Control', 1, 2.0, 'seedling emerged')
    exp.record('Treatment', 1, 2.0, 'seedling emerged')
    exp.record('Control', 7, 5.2, 'true leaves')
    exp.record('Treatment', 7, 6.8, 'true leaves')
    print()
    print(exp.summary())
    exp.export_csv('demo_export.csv')


if __name__ == '__main__':
    demo()
