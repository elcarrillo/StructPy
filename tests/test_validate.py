import pandas as pd
import pytest
import logging
import sys
from structpy.validate import validate_data, validate_file, summarize
from structpy import main

# Mock configuration for testing
MOCK_CONFIG = {
    "validation": {
        "check_missing_values": True,
        "check_duplicate_columns": True,
        "check_outliers": True,
        "missing_value_threshold": 0.1  # 10%
    }
}

@pytest.fixture
def mock_config(monkeypatch):
    """Fixture to mock the configuration loader."""
    monkeypatch.setattr("structpy.validate.load_config", lambda: MOCK_CONFIG)

def test_validate_empty_dataframe(mock_config, caplog):
    """Test validation on an empty DataFrame."""
    df = pd.DataFrame()
    with caplog.at_level(logging.WARNING):
        results = validate_data(df)
    assert "The DataFrame is empty. Validation skipped." in caplog.text
    assert results["missing_values"] is False
    assert results["duplicate_columns"] is False
    assert not results["outliers"]

def test_validate_missing_values(mock_config, caplog):
    """Test validation for missing values."""
    df = pd.DataFrame({"A": [1, None, 3], "B": [4, 5, None]})  # 33.33% missing values
    with caplog.at_level(logging.WARNING):
        results = validate_data(df)
    assert "Missing values exceed threshold" in caplog.text
    assert results["missing_values"] is True

def test_validate_duplicate_columns(mock_config, caplog):
    """Test validation for duplicate columns."""
    # A dict can't hold two "A" keys, so pass the column names separately
    df = pd.DataFrame([[1, 4], [2, 5], [3, 6]], columns=["A", "A"])  # Duplicate columns
    with caplog.at_level(logging.ERROR):  # Expect ERROR level logging
        results = validate_data(df)
    assert "Duplicate column names found" in caplog.text, "Expected duplicate column log not found."
    assert results["duplicate_columns"] is True, "Duplicate column result not updated."
    assert results["duplicate_names"] == ["A"]
    assert results["passed"] is False


def test_validate_outliers(mock_config, caplog):
    """Test validation for outliers."""
    # Needs enough points for 100 to fall outside 1.5 * IQR
    df = pd.DataFrame({"A": [1, 2, 3, 4, 100], "B": [4, 5, 6, 7, 8]})  # Outlier in column A
    with caplog.at_level(logging.WARNING):  # Expect WARNING level logging
        results = validate_data(df)
    assert "Outliers detected in column 'A'" in caplog.text, "Expected outlier log not found."
    assert "A" in results["outliers"], "Outlier column not added to results."
    assert results["passed"] is True, "Outliers alone should not fail validation."


def test_validate_no_issues(mock_config, caplog):
    """Test validation on a clean DataFrame."""
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    with caplog.at_level(logging.INFO):
        results = validate_data(df)
    assert "Data validation complete." in caplog.text
    assert results["missing_values"] is False
    assert results["duplicate_columns"] is False
    assert not results["outliers"]

def test_validate_no_issues_passes(mock_config):
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    assert validate_data(df)["passed"] is True

def test_validate_empty_fails(mock_config):
    results = validate_data(pd.DataFrame())
    assert results["empty"] is True
    assert results["passed"] is False

def test_validate_one_empty_column_is_caught(mock_config, caplog):
    """One fully empty column out of ten is only 10% missing overall, but should still be flagged."""
    data = {f"c{i}": [1, 2, 3, 4] for i in range(9)}
    data["empty"] = [None] * 4
    with caplog.at_level(logging.WARNING):
        results = validate_data(pd.DataFrame(data))
    assert results["missing_values"] is True
    assert results["missing_columns"] == {"empty": 1.0}
    assert "'empty' (100%)" in caplog.text
    assert results["passed"] is False

def test_validate_missing_under_threshold_passes(mock_config):
    """A column at or under the threshold (10% here) is fine."""
    df = pd.DataFrame({"A": [1, 2, 3, 4, 5, 6, 7, 8, 9, None], "B": range(10)})
    results = validate_data(df)
    assert results["missing_values"] is False
    assert results["passed"] is True

# --- Files ---

def test_validate_file_duplicate_header(mock_config, tmp_path):
    """pandas renames a repeated header to A.1; the raw header still catches it."""
    path = tmp_path / "dup.csv"
    path.write_text("A,B,A\n1,2,3\n4,5,6\n")
    results = validate_file(str(path))
    assert results["duplicate_names"] == ["A"]
    assert results["passed"] is False

def test_validate_file_header_only(mock_config, tmp_path):
    path = tmp_path / "header_only.csv"
    path.write_text("A,B\n")
    assert validate_file(str(path))["empty"] is True

def test_validate_file_completely_empty(mock_config, tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("")
    assert validate_file(str(path))["empty"] is True

def test_summarize():
    results = {
        "passed": False, "empty": False, "missing_values": True,
        "missing_columns": {"temp": 0.6}, "duplicate_columns": True,
        "duplicate_names": ["A"], "outliers": ["velocity"],
    }
    assert summarize(results, "data.csv") == (
        "Validation FAILED: data.csv\n"
        "  - Too many missing values in: 'temp' (60%)\n"
        "  - Duplicate column names: 'A'\n"
        "  - Outliers (warning only) in: 'velocity'"
    )

# --- Command line ---

def run_cli(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["structpy", *args])
    with pytest.raises(SystemExit) as exc:
        main.main()
    return exc.value.code

def test_cli_validate_pass(mock_config, tmp_path, monkeypatch, capsys):
    path = tmp_path / "good.csv"
    path.write_text("A,B\n1,4\n2,5\n3,6\n")
    assert run_cli(monkeypatch, "validate", "--file", str(path)) == 0
    assert capsys.readouterr().out.startswith("Validation PASSED")

def test_cli_validate_fail(mock_config, tmp_path, monkeypatch, capsys):
    path = tmp_path / "bad.csv"
    path.write_text("A,A\n1,4\n2,5\n")
    assert run_cli(monkeypatch, "validate", "--file", str(path)) == 1
    out = capsys.readouterr().out
    assert out.startswith("Validation FAILED")
    assert "Duplicate column names: 'A'" in out

def test_cli_validate_missing_file(tmp_path, monkeypatch, capsys):
    assert run_cli(monkeypatch, "validate", "--file", str(tmp_path / "nope.csv")) == 2
    assert "file not found" in capsys.readouterr().err

@pytest.mark.parametrize("action", ["create_dirs", "backup", "validate"])
def test_cli_missing_required_option(action, monkeypatch, capsys):
    assert run_cli(monkeypatch, action) == 2
    assert "required" in capsys.readouterr().err
