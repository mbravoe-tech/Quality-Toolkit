# Quality-Toolkit

A Python toolkit for inspecting the quality of tabular datasets.

## Features
- Command-line interface for generating markdown quality reports.
- Library API surfaces per-column metrics, missing-value ratios, and duplicate counts.
- Extensible structure ready for additional quality checks and integrations.

## Getting Started
1. Create a virtual environment and install the project in editable mode:
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # PowerShell
   pip install -e .[dev]
   ```
   On systems with strict PowerShell policies, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` before activation, or use Command Prompt with `\.venv\Scripts\activate.bat`.
2. Run the CLI against a CSV file:
   ```bash
   quality-toolkit path\to\data.csv
   ```

## Library Example
```python
import pandas as pd
from quality_toolkit import evaluate_data_quality

frame = pd.read_csv("path/to/data.csv")
report = evaluate_data_quality(frame)
print(report.row_count)
```

## Tests
```bash
pytest
```
