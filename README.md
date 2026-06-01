# Controlled Experiment Demo

A minimal, reproducible, and verifiable controlled experiment template.

This project demonstrates the core principles of scientific controlled experiments through a simple plant growth simulation. Everything runs on pure Python with zero external dependencies.

## Quick Start



## Default Results (seed=42, 14 days)

| Metric | Control (2-day) | Treatment (daily) | Difference |
|--------|----------------|-------------------|------------|
| Final height | 12.57 cm | 14.96 cm | +2.39 cm (+19%%) |

## Project Files

- simulate_experiment.py - Run the controlled experiment simulation
- experiment.py - Real data recording and analysis tool
- plot_results.py - Visualize results as chart or table
- verify_results.py - Assert results match expected values
- analyze.py - Statistical difference analysis between groups
- LICENSE - MIT License

## Design Principles

1. Zero dependencies - pure Python standard library only
2. Reproducible - fixed random seed
3. Verifiable - built-in assertions
4. Minimal - each file does one thing

## License

MIT - see LICENSE.

---

Also available in Chinese (README.zh.md).
