# Quality Toolkit Overview

Quality Toolkit offers a quick way to assess the condition of tabular datasets. The suite now includes a desktop application, a CLI, and a Python API so you can choose the workflow that fits best.

## Desktop app

Launch the interactive window with `quality-toolkit-gui`, open a CSV, Excel, or Parquet file, and pick the columns you care about. The app shows row counts, duplicate detection, column-level missing ratios, and a ready-to-share markdown report.

## Command line

```bash
quality-toolkit path/to/data.csv
```

## Python API

```python
from quality_toolkit import evaluate_data_quality

quality = evaluate_data_quality(dataframe)
```

