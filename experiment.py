#!/usr/bin/env python3
"""experiment.py - 对照实验数据记录与分析工具

这是一个用于记录和分析真实实验数据的工具。
与 simulate 类脚本不同，它假设你已经有了观测数据，
负责录入、汇总、对比分析和导出。
"""

import csv
from datetime import datetime


class Experiment:
    """对照实验记录类"""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.created_at = datetime.now()
        self.groups = {}

    def add_group(self, name: str, condition: str):
        if name not in self.groups:
            self.groups[name] = []
            print(f"[组] 添加组 '{name}': {condition}")
            return True
        print(f"[警告] 组 '{name}' 已存在")
        return False

    def record(self, group: str, day: int, value: float, note: str = ""):
        if group not in self.groups:
            print(f"[错误] 组 '{group}' 不存在，请先调用 add_group")
            return False
        rec = {"day": day, "value": value, "note": note,
               "ts": datetime.now().isoformat()}
        self.groups[group].append(rec)
        print(f"[记录] 第{day}天 | {group}: {value} {note}")
        return True

    def summary(self) -> str:
        NL = chr(10)
        lines = [f"实验名称: {self.name}"]
        if self.description:
            lines.append(f"描述: {self.description}")
        lines.append(f"组数: {len(self.groups)}")
        lines.append("")
        for gname, records in self.groups.items():
            lines.append(f"--- {gname} ---")
            if not records:
                lines.append("  (无数据)")
                continue
            vals = [r["value"] for r in records]
            days = [r["day"] for r in records]
            lines.append(f"  记录数: {len(records)}")
            lines.append(f"  天数: {min(days)} - {max(days)}")
            lines.append(f"  最新值: {vals[-1]}")
            if len(vals) > 1:
                lines.append(f"  总变化: {vals[-1] - vals[0]:+.2f}")
            lines.append("")
        return NL.join(lines)

    def export_csv(self, path: str):
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["组名", "天数", "观测值", "备注", "记录时间"])
            for gname, records in self.groups.items():
                for r in sorted(records, key=lambda x: x["day"]):
                    w.writerow([gname, r["day"], r["value"], r["note"], r["ts"]])
        print(f"已导出: {path}")


def demo():
    print("=" * 50)
    print("experiment.py - 实验数据记录工具")
    print("=" * 50)
    exp = Experiment("浇水频率对照", "记录真实观测数据")
    exp.add_group("对照组", "每2天浇水")
    exp.add_group("实验组", "每天浇水")
    exp.record("对照组", 1, 2.0, "种子出土")
    exp.record("实验组", 1, 2.0, "种子出土")
    exp.record("对照组", 7, 5.2, "真叶展开")
    exp.record("实验组", 7, 6.8, "真叶展开")
    print()
    print(exp.summary())
    exp.export_csv("demo_export.csv")


if __name__ == "__main__":
    demo()
