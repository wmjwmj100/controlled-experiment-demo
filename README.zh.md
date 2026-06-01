# 对照实验示例项目

一个最小可验证的对照实验骨架——零依赖，一个 Python 脚本，一条命令运行。

```bash
python3 simulate_experiment.py
```

**默认结果（种子 42，14 天）：** 实验组（每天浇水）比对照组（每 2 天浇水）增长 **约 19%**。

## 为什么做这个

科学思维从对照实验开始。这个项目提供了一个**微小但完整、可验证**的骨架，可以直接运行、修改和扩展——不需要 Jupyter、不需要 scipy、不需要任何安装。适合：

- **学生**学习实验设计
- **教师**课堂演示
- **研究者**在正式编码前快速原型

## 快速开始

```bash
python3 simulate_experiment.py
```

输出 `results.csv`，包含两组植物每天的测量数据。

自定义参数：
```bash
python3 simulate_experiment.py --days 30 --output my_data.csv --seed 123
```

## 文件说明

| 文件 | 用途 |
|------|------|
| `simulate_experiment.py` | 核心模拟脚本——可配置、可复现、零依赖 |
| `analyze.py` | 读取 CSV 结果，计算分组统计量和组间对比 |
| `plot_results.py` | 可视化结果——折线图（需 matplotlib）或表格模式 |
| `experiment.py` | 记录**真实观测数据**：建组、按天记录、出摘要、导出 CSV |
| `verify_results.py` | 断言默认输出符合预期值 |
| `test_simulate.py` | 单元测试（11 个测试，零依赖） |

### 分析结果

```bash
python3 analyze.py results.csv
```

### 可视化

```bash
python3 plot_results.py results.csv
```

### 记录真实数据

```python
from experiment import Experiment

exp = Experiment("我的实验")
exp.add_group("对照组", "标准条件")
exp.add_group("实验组", "修改条件")
exp.record("对照组", 1, 2.5)
exp.record("实验组", 1, 2.5)
print(exp.summary())
exp.export_csv("my_data.csv")
```

## 设计原则

1. **零摩擦**——纯 Python 标准库，无需 pip install
2. **验证优先**——相同种子产生相同结果，有断言和测试保证
3. **真实数据可用**——experiment.py 适用于实际观测场景
4. **小巧完整**——模拟、分析、可视化、验证在一个地方

## 许可证

MIT
