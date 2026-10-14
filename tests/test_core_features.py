import os
from datetime import datetime
import pytest
import time  

from structpy.core_features import create_project_dirs, generate_filename

# Helper function to validate directory structure
def check_directory_structure(base_path, structure):
    """Validate the directory structure."""
    for folder, subfolders in structure.items():
        folder_path = base_path / folder
        assert folder_path.exists(), f"Missing directory: {folder} (Expected path: {folder_path})"
        for subfolder in subfolders:
            subfolder_path = folder_path / subfolder
            assert subfolder_path.exists(), f"Missing subdirectory: {subfolder} (Expected path: {subfolder_path})"

def test_create_project_dirs(tmp_path):
    """Test creating a project directory structure."""
    base_path = tmp_path / "test_project"
    create_project_dirs(base_path)

    # Check directory structure
    expected_structure = {
        "input": [],
        "output": ["plots", "tables"],
        "logs": [],
        "temp": []
    }
    check_directory_structure(base_path, expected_structure)

    # Ensure no unexpected directories
    unexpected_dirs = list(base_path.glob("*"))
    assert len(unexpected_dirs) == len(expected_structure), (
        f"Unexpected directories created. Expected {len(expected_structure)}, found {len(unexpected_dirs)}"
    )

def test_create_project_dirs_existing(tmp_path):
    """Test creating directories when some already exist."""
    base_path = tmp_path / "test_project"
    os.makedirs(base_path / "input")  # Pre-create a directory
    create_project_dirs(base_path)

    # Ensure it doesn't overwrite existing directories
    assert (base_path / "input").exists(), "Existing directory 'input' was overwritten."
    assert (base_path / "output" / "plots").exists(), "Subdirectory 'plots' under 'output' was not created."

def test_generate_filename():
    """Test generating filenames with default and custom values."""
    filename = generate_filename("test", "txt")

    # Check prefix and extension
    assert filename.startswith("test_"), f"Filename prefix does not match. Got: {filename}"
    assert filename.endswith(".txt"), f"Filename extension does not match. Got: {filename}"

    # Extract timestamp and unique ID
    name_parts = filename.split("_", 1)[1].rsplit(".", 1)[0].split("-")
    timestamp_str = "-".join(name_parts[:2])  # Join date and time
    unique_id = name_parts[2]

    # Check timestamp format
    try:
        datetime.strptime(timestamp_str, "%Y%m%d-%H%M%S")
    except ValueError:
        pytest.fail(f"Timestamp format is invalid. Got: {timestamp_str}, expected format: YYYYMMDD-HHMMSS")

    # Ensure unique ID is 6 characters
    assert len(unique_id) == 6, f"Unique ID length is incorrect. Got: {unique_id}"

    # Check uniqueness
    filename2 = generate_filename("test", "txt")
    assert filename != filename2, "Generated filenames are not unique."

def test_generate_filename_edge_cases():
    """Test filename generation with unusual parameters."""
    # Empty prefix and unusual extension
    filename = generate_filename("", "log")
    assert filename.startswith("_"), f"Filename does not start with an underscore for an empty prefix. Got: {filename}"
    assert filename.endswith(".log"), f"Filename extension does not match. Got: {filename}"

    # Very long prefix
    long_prefix = "a" * 100
    filename = generate_filename(long_prefix, "csv")
    assert filename.startswith(long_prefix), f"Filename prefix does not match for long prefix. Got: {filename}"
    assert filename.endswith(".csv"), f"Filename extension does not match. Got: {filename}"
