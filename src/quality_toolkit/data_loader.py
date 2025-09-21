from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Optional

import pandas as pd


def load_dataset(
    path: str | Path,
    *,
    dtype: Optional[Dict[str, str]] = None,
    encoding: str = "utf-8",
    delimiter: Optional[str] = None,
) -> pd.DataFrame:
    """Load a tabular file into a :class:`pandas.DataFrame`."""

    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(f"Dataset not found: {target}")

    suffix = target.suffix.lower()
    if suffix in {".csv", ".txt", ".tsv"}:
        resolved_delimiter = delimiter or _detect_delimiter(target)
        return pd.read_csv(target, dtype=dtype, encoding=encoding, delimiter=resolved_delimiter)
    if suffix in {".parquet"}:
        return pd.read_parquet(target)

    raise ValueError(f"Unsupported file type: {suffix}")


def _detect_delimiter(path: Path, sample_bytes: int = 8192) -> str:
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        sample = handle.read(sample_bytes)

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        return dialect.delimiter
    except csv.Error:
        return ","
