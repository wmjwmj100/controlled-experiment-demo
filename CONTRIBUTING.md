# Contributing

This is a community project from the Virtual Town. Everyone is welcome to
improve it — whether you're fixing a bug, adding a feature, or improving docs.

## How to contribute

1. **Run the tests** before and after your changes:
   ```bash
   python3 -m unittest test_simulate.py -v
   ```

2. **Keep it zero-dependency.** All core functionality must use only Python
   standard library. Optional features (like matplotlib-based plotting) are
   fine behind a try/except.

3. **Keep results reproducible.** If you add a new simulation feature,
   ensure it accepts a `--seed` parameter for fixed-random-seed runs.

4. **Update the README** if you add, remove, or change files or usage.

5. **Commit messages** should be clear and reference what changed and why.

## Code of conduct

Be constructive. Assume good intent. This is a learning and teaching project.
