from __future__ import annotations

from .analysis import DatasetQuality


def build_markdown_report(dataset_quality: DatasetQuality) -> str:
    """Return a markdown representation of ``dataset_quality``."""

    lines: list[str] = ["# Data Quality Report", ""]
    lines.extend(_build_overview(dataset_quality))
    lines.append("")
    lines.extend(_build_column_section(dataset_quality))

    if dataset_quality.warnings:
        lines.append("")
        lines.append("## Warnings")
        for warning in dataset_quality.warnings:
            lines.append(f"- {warning}")

    return "\n".join(lines).strip() + "\n"


def _build_overview(dataset_quality: DatasetQuality) -> list[str]:
    return [
        "| Metric | Value |",
        "| --- | --- |",
        f"| Rows | {dataset_quality.row_count} |",
        f"| Duplicate rows | {dataset_quality.duplicate_rows} |",
    ]


def _build_column_section(dataset_quality: DatasetQuality) -> list[str]:
    if not dataset_quality.columns:
        return ["## Columns", "", "_No columns detected._"]

    lines = [
        "## Columns",
        "",
        "| Name | Dtype | Missing | Distinct | Samples |",
        "| --- | --- | --- | --- | --- |",
    ]

    for name, column in dataset_quality.columns.items():
        missing_display = f"{column.missing_count} ({column.missing_ratio:.1%})"
        sample_display = ", ".join(column.sample_values[:5]) if column.sample_values else "—"
        lines.append(
            f"| {name} | {column.dtype} | {missing_display} | {column.distinct_count} | {sample_display} |"
        )

    return lines
