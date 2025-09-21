"""Quality Toolkit package providing reusable data quality helpers."""

from .analysis import ColumnQuality, DatasetQuality, evaluate_data_quality
from .data_loader import load_dataset
from .report import build_markdown_report

__all__ = [
    "ColumnQuality",
    "DatasetQuality",
    "evaluate_data_quality",
    "load_dataset",
    "build_markdown_report",
]

__version__ = "0.1.0"
