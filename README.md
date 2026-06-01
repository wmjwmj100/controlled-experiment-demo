# Controlled Experiment Demo

> A minimal, reproducible, and verifiable controlled experiment toolkit.
> 一个最小可复现、可验证的对照实验工具集。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## Why This Project

Understanding controlled experiments is fundamental to scientific thinking. This project provides a **zero-dependency** Python toolkit that:

- Simulates a controlled experiment (watering frequency vs. plant growth) with **fixed random seeds** for exact reproducibility
- Lets you **record real observation data** with the `Experiment` class
- **Verifies** simulation outputs match expected results
- **Analyzes** differences between control and treatment groups
- **Visualizes** growth curves (with or without matplotlib)

Perfect for learning, teaching, or as a starting point for real experiments.

## Quick Start

```bash
# 1. Run the simulation (generates results.csv)
python3 simulate_experiment.py

# 2. Verify the results match expectations
python3 verify_results.py
# Expected output: ok

# 3. Analyze the differences
python3 analyze.py --csv results.csv

# 4. Visualize (basic table mode, no matplotlib needed)
python3 plot_results.py results.csv

# 5. Run unit tests (all should pass)
python3 -m unittest test_simulate.py -v
```

## Default Results (seed=42, 14 days)

| Group | Watering | Final Height |
|-------|----------|-------------|
| Control | Every 2 days | **12.57 cm** |
| Treatment | Every day | **14.96 cm** |
| Difference | — | **+2.39 cm (+19.0%)** |

## Project Structure

| File | Description |
|------|-------------|
| `simulate_experiment.py` | Core simulation — generates reproducible CSV results with configurable days/seed/output |
| `experiment.py` | Record real observation data using the `Experiment` class, generate summaries, export CSV |
| `verify_results.py` | Lightweight assertion — checks final heights match expected values, prints "ok" |
| `analyze.py` | Statistical analysis — computes means, std devs, growth rates, difference significance |
| `plot_results.py` | Visualization — table mode (no deps) or matplotlib line chart |
| `test_simulate.py` | Unit tests — 11 tests covering reproducibility, edge cases, and CLI output (unittest) |
| `pyproject.toml` | Package metadata for PyPI or downstream packaging |
| `LICENSE` | MIT License |
| `.gitignore` | Python cache and generated file exclusions |
| `results.csv` | Sample output from default simulation run |
| `results.png` | Sample plot (generated if matplotlib is available) |

## Customization

```bash
# 30-day experiment with custom seed
python3 simulate_experiment.py --days 30 --seed 123 --output my_results.csv

# Analyze custom output
python3 analyze.py --csv my_results.csv

# Plot with matplotlib (if installed)
pip install matplotlib
python3 plot_results.py results.csv --output my_plot.png
```

## Design Principles

1. **Zero external dependencies** — Pure Python standard library. Run it anywhere.
2. **Reproducible by default** — Fixed random seeds ensure identical results across runs.
3. **Verifiable** — Every claim comes with a check script or test.
4. **Minimal and clear** — Each file has one job. Easy to read, modify, and extend.

## 项目说明（中文）

### 实验设定
- **初始条件**：两组植物初始高度均为 2.0 cm
- **单一变量**：浇水频率
  - 对照组：每 2 天浇水一次
  - 实验组：每天浇水一次
- **观察周期**：连续 14 天

### 快速开始
```bash
# 生成模拟数据
python3 simulate_experiment.py

# 验证结果
python3 verify_results.py

# 分析差异
python3 analyze.py --csv results.csv

# 查看图表（纯文本模式）
python3 plot_results.py results.csv

# 运行测试
python3 -m unittest test_simulate.py -v
```

### 自定义参数
```bash
python3 simulate_experiment.py --days 30 --output my_results.csv --seed 123
```

### experiment.py 用法
适合记录真实观测数据：
```python
from experiment import Experiment
exp = Experiment("实验名称")
exp.add_group("对照组", "每2天浇水")
exp.record("对照组", 1, 2.0, "种子出土")
print(exp.summary())
exp.export_csv("data.csv")
```

## License

MIT — see [LICENSE](LICENSE).
