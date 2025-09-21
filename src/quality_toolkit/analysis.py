from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pandas as pd


@dataclass(frozen=True)
class ColumnQuality:
    """Describes quality characteristics tracked per column."""

    dtype: str
    missing_count: int
    missing_ratio: float
    distinct_count: int
    sample_values: List[str]


@dataclass(frozen=True)
class DatasetQuality:
    """Aggregated dataset quality metrics."""

    row_count: int
    duplicate_rows: int
    columns: Dict[str, ColumnQuality]
    warnings: List[str]


def evaluate_data_quality(df: pd.DataFrame, sample_size: int = 5) -> DatasetQuality:
    """Inspect ``df`` and return core quality indicators."""

    if sample_size <= 0:
        raise ValueError("sample_size must be positive")

    row_count = int(len(df))
    duplicate_rows = int(df.duplicated().sum()) if row_count else 0
    warnings: List[str] = []
    columns: Dict[str, ColumnQuality] = {}

    if row_count == 0:
        warnings.append("Dataset contains no rows.")

    for column in df.columns:
        series = df[column]
        missing_count = int(series.isna().sum())
        missing_ratio = float(missing_count / row_count) if row_count else 0.0
        distinct_count = int(series.nunique(dropna=True))
        sample_candidates = series.dropna().unique()[:sample_size]
        sample_values = [_format_value(value) for value in sample_candidates]

        columns[column] = ColumnQuality(
            dtype=str(series.dtype),
            missing_count=missing_count,
            missing_ratio=round(missing_ratio, 4),
            distinct_count=distinct_count,
            sample_values=sample_values,
        )

        if missing_ratio > 0.3:
            warnings.append(
                f"Column '{column}' has {missing_ratio:.0%} missing values."
            )

    return DatasetQuality(
        row_count=row_count,
        duplicate_rows=duplicate_rows,
        columns=columns,
        warnings=warnings,
    )


def calculate_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Return numeric summary statistics for ``df``."""

    if df.empty:
        raise ValueError("Cannot compute summary statistics on an empty DataFrame")

    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        raise ValueError("DataFrame does not contain numeric columns")

    summary = numeric_df.describe().transpose()
    summary["missing_count"] = numeric_df.isna().sum()
    summary["missing_ratio"] = summary["missing_count"] / len(df)
    return summary


def _format_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)
