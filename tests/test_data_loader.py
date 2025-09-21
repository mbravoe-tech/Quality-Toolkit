import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from quality_toolkit.data_loader import load_dataset


def test_load_dataset_supports_excel(tmp_path):
    frame = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    path = tmp_path / "sample.xlsx"
    frame.to_excel(path, index=False)

    loaded = load_dataset(path)

    assert_frame_equal(loaded, frame)


def test_load_dataset_rejects_unknown_extension(tmp_path):
    path = tmp_path / "unknown.xyz"
    path.write_text("dummy")

    with pytest.raises(ValueError):
        load_dataset(path)
