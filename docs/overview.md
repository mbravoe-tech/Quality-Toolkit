# Quality Toolkit Overview

Quality Toolkit offers a quick way to assess the condition of tabular datasets. Load a CSV file and the CLI reports record counts, duplicate detection, missing-value ratios, and per-column samples.

```bash
quality-toolkit path/to/data.csv
```

The project also exposes a Python API via `quality_toolkit.evaluate_data_quality` if you need to embed the checks into larger workflows.
