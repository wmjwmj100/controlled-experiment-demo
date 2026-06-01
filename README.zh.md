# 对照实验示例项目

这个项目是最小可验证对照实验的骨架。

## 实验设定
- 初始条件：两组植物初始高度都为 2.0 cm
- 变量：浇水频率
  - 对照组：每 2 天浇水一次
  - 实验组：每天浇水一次
- 观察：连续 14 天的植物高度变化

## 当前文件
- simulate_experiment.py：模拟脚本，固定随机种子，结果可复现
- experiment.py：实验数据记录与分析工具，录入真实数据、生成摘要、导出 CSV
- results.csv：运行脚本后生成的实验数据表
- README.md：本文件

## 运行方式
生成模拟数据：
python3 simulate_experiment.py

自定义参数：
python3 simulate_experiment.py --days 30 --output my_results.csv --seed 123

## experiment.py 用法
适合记录真实观测数据。运行示例：
python3 experiment.py

在代码中调用：
from experiment import Experiment
exp = Experiment("实验名称")
exp.add_group("对照组", "条件说明")
exp.record("对照组", 1, 2.5, "备注")
print(exp.summary())
exp.export_csv("data.csv")

## 原则
保持轻量，把可验证放在最前面。
