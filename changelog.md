# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]
### Added
- None
---

## [v0.2.0] - Unreleased
### Added
- StructPy is now an installable package: `import structpy`, `python -m structpy`, and `pyproject.toml` in place of `setup.py`.
- `--config` option on every command to use a specific config file.
- Each command has its own options and help (`structpy backup --help`).
- `validate_file()` for CSV files, and a PASSED/FAILED summary from `structpy validate`.

### Changed
- Works from any folder: built-in defaults, overridden by `config.yaml` in the current folder.
- Backups are named `<name>_<timestamp>-<id>.zip` and never overwrite earlier ones; earlier StructPy backups inside the folder are skipped.
- Missing values are checked per column against the threshold.
- `structpy validate` exits 0 on pass, 1 on fail; usage errors exit 2.
- `generate_filename` on the command line uses the `filename` defaults from the config.
- Importing StructPy no longer configures logging; only the command-line tool does.
- Requires Python 3.9 or newer.

### Fixed
- `--archive name.zip` no longer produces `name.zip.zip`.
- Duplicate column names are detected in CSV headers (pandas renames them on read).
---

## [v0.1.0] - 2024-11-30
### Added
- **Initial release** of StructPy, a Python-based tool for managing academic data projects, aimed at simplifying workflows for researchers and data practitioners.
- **Directory Creation**:
  - Automatically generate project directory structures based on customizable YAML configurations.
- **File Naming**:
  - Generate unique, timestamped filenames with user-defined prefixes and extensions.
- **Dataset Validation**:
  - Validate datasets for:
    - Missing values, with configurable thresholds.
    - Duplicate column names.
    - Numeric outliers based on IQR (Interquartile Range).
- **Backup Utility**:
  - Compress project directories into `.zip` archives for safekeeping and sharing.
- **Configurable Settings**:
  - Support for YAML configuration files to customize tool behavior.
- **Command-Line Interface (CLI)**:
  - Easy-to-use CLI for all core functionalities:
    - `create_dirs`: Automatically create nested project directories.
    - `generate_filename`: Create unique, descriptive filenames for files.
    - `validate`: Analyze datasets for structural issues or anomalies.
    - `backup`: Archive project files into `.zip` for easy sharing.
- **Unit Tests**:
  - Comprehensive test coverage for core features:
    - Directory creation (`create_dirs`).
    - Filename generation (`generate_filename`).
