import pandas as pd
import pytest

from quality_toolkit.analysis import calculate_summary_statistics, evaluate_data_quality


def test_evaluate_data_quality_basic_metrics():
    frame = pd.DataFrame(
        {
            "score": [10, 12, None, 8],
            "label": ["A", "A", "B", "B"],
        }
    )

    result = evaluate_data_quality(frame, sample_size=2)

    assert result.row_count == 4
    assert result.duplicate_rows == 0
    score_column = result.columns["score"]
    assert score_column.missing_count == 1
    assert score_column.missing_ratio == pytest.approx(0.25)
    assert score_column.distinct_count == 3
    assert len(score_column.sample_values) <= 2


def test_evaluate_data_quality_high_missing_marks_warning():
    frame = pd.DataFrame({"value": [1, None, None, None]})

    result = evaluate_data_quality(frame)

    assert any("missing values" in warning for warning in result.warnings)


def test_evaluate_data_quality_rejects_invalid_sample_size():
    frame = pd.DataFrame({"value": [1, 2, 3]})

    with pytest.raises(ValueError):
        evaluate_data_quality(frame, sample_size=0)


def test_calculate_summary_statistics_includes_missing_columns():
    frame = pd.DataFrame({"value": [1, None, 3, 4]})

    summary = calculate_summary_statistics(frame)

    assert "missing_count" in summary.columns
    assert summary.loc["value", "missing_count"] == 1


def test_calculate_summary_statistics_requires_numeric():
    frame = pd.DataFrame({"label": ["a", "b"]})

    with pytest.raises(ValueError):
        calculate_summary_statistics(frame)
