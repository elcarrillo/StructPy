<p align="center">
  <img src="./logo.png" alt="StructPy Logo" width="400"/>
</p>

# **StructPy**

StructPy is a Python-based command-line tool designed for academics and scientists to manage data projects effectively. It simplifies workflows by creating structured project directories, generating timestamped filenames, validating datasets, and backing up projects seamlessly.

---

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/elcarrillo/StructPy)](https://github.com/elcarrillo/StructPy)
[![Open Issues](https://img.shields.io/github/issues/elcarrillo/StructPy)](https://github.com/elcarrillo/StructPy/issues)
[![Stars](https://img.shields.io/github/stars/elcarrillo/StructPy?style=social)](https://github.com/elcarrillo/StructPy/stargazers)
[![Code Quality](https://img.shields.io/codefactor/grade/github/elcarrillo/StructPy)](https://www.codefactor.io/repository/github/elcarrillo/StructPy)
![Build Status](https://github.com/elcarrillo/StructPy/actions/workflows/ci.yml/badge.svg)

## **Features**

1. **Create Project Directory Structures**:
   - Automatically generate consistent directories and subdirectories based on a YAML configuration file.
2. **Generate Filenames**:
   - Create unique, timestamped filenames with customizable prefixes and extensions.
3. **Validate Datasets**:
   - Check for missing values, duplicate columns, and outliers in CSV files.
4. **Backup Projects**:
   - Compress entire project directories into `.zip` archives for easy sharing and safekeeping.

...

# **StructPy**

StructPy is a Python-based command-line tool designed for academics and scientists to manage data projects effectively. It simplifies workflows by creating structured project directories, generating timestamped filenames, validating datasets, and seamlessly backing up projects.

---

## **Features**
1. **Create Project Directory Structures**:
   - Automatically generate consistent directories and subdirectories based on a YAML configuration file.
2. **Generate Filenames**:
   - Create unique, timestamped filenames with customizable prefixes and extensions.
3. **Validate Datasets**:
   - Check for missing values, duplicate columns, and outliers in CSV files.
4. **Backup Projects**:
   - Compress entire project directories into `.zip` archives for easy sharing and safekeeping.

---

## **Installation**

1. Clone the repository:
   ```bash
   git clone https://github.com/elcarrillo/StructPy.git
   cd StructPy
   ```

2. Install the package in editable mode using `setup.py`:
   ```bash
   pip install -e .
   ```

3. Verify installation:
   ```bash
   structpy --help
   ```

---

## **File Structure**

The following is the structure of the project:

```
StructPy/
├── src/                     # Source code
│   ├── __init__.py
│   ├── main.py
│   ├── core_features.py
│   ├── validate.py
│   ├── config_loader.py
├── tests/                   # Unit tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_core_features.py
├── examples/                # Example configurations/files
│   └── ...
├── .gitignore               # Git ignore rules
├── LICENSE                  # License file
├── README.md                # Project documentation
├── requirements.txt         # Project dependencies
├── pytest.ini               # Pytest configuration
├── setup.py                 # Installation script
├── logo.png                 # package logo
├── config.yaml              # Main configuration file
├── CHANGELOG.md             # changelog


```

---

## **Configuration**

StructPy works out of the box with built-in defaults (shown below). To customize it, put a `config.yaml` in the folder you run `structpy` from. A `directories` section replaces the default layout; other sections only override the settings they list.

**Example `config.yaml`:**
```yaml
directories:
  input: []
  output:
    - plots
    - tables
  logs: []
  temp: []

backup:
  default_archive_name: "project_backup"

filename:
  default_prefix: "datafile"
  default_extension: "csv"

validation:
  check_missing_values: true
  check_duplicate_columns: true
  missing_value_threshold: 0.1  # Allow up to 10% missing values
```

---

## **Usage**

To use the tool via the command-line interface, run the `structpy` command. The syntax follows this format:

```
structpy {positional_argument} [--option OPTION_PARAMETER]
```

For a complete list of positional arguments and available options, use the `--help` flag:

```
structpy --help
```

Here are some examples of typical workflows to get you started:

### **1. Create Project Directories**
```bash
structpy create_dirs --path ./experiment_001
```

**Result:**
The following directory structure is created at `./experiment_001`:
```
experiment_001/
├── input/
├── output/
│   ├── plots/
│   ├── tables/
├── logs/
├── temp/
```

---

Configured directory names must be relative paths inside the project. Absolute paths, parent traversal (`..`), and symlinks leading outside the project are rejected before any directories are created.

### **2. Generate Filenames**

```bash
structpy generate_filename --prefix results --ext csv
```

**Output:**
```
Generated filename: results_20241121-153200.csv
```

You can customize the prefix and extension using the command-line arguments or rely on defaults from `config.yaml`.

Without command-line overrides or a configuration file, the prefix is `datafile` and the extension is `csv`.

---

### **3. Validate a Dataset**
```bash
structpy validate --file data.csv
```

**Example Output:**
```
Validation FAILED: data.csv
  - Too many missing values in: 'temp' (60%)
  - Duplicate column names: 'id'
  - Outliers (warning only) in: 'velocity'
```

Validation fails if the file has no data rows, any column's share of missing values is above `missing_value_threshold`, or a column name repeats. Outliers are reported but don't fail it. The command exits with code 0 on pass and 1 on fail, so scripts can check it (e.g. `structpy validate --file data.csv && run_analysis`).

For machine-readable results, use `structpy validate --file data.csv --json`.
This prints the validation results as a JSON object and keeps the same exit codes.
Diagnostic logs go to stderr, so stdout can be redirected to a report file.

---

### **4. Backup a Project**
```bash
structpy backup --path ./experiment_001 --archive experiment_backup
```

**Result:**
The project is compressed into a timestamped archive such as `experiment_backup_20241121-154500-a1b2c3.zip`, so earlier backups are never overwritten. Without `--archive`, the name comes from `default_archive_name` in the config.

The source path must be an existing directory; invalid paths are rejected before an archive is created.

---

## **Advanced Usage Example**

### **Scenario**: Managing a Collaborative Research Project

In this scenario, StructPy is used to manage multiple experiments within a single project folder.

1. **Initialize the Project:**
   Create a base directory for the project:
   ```bash
   structpy create_dirs --path ./collaborative_project
   ```

   Resulting structure:
   ```
   collaborative_project/
   ├── input/
   ├── output/
   │   ├── plots/
   │   ├── tables/
   ├── logs/
   ├── temp/
   ```

2. **Run Multiple Experiments:**
   Create subdirectories for each experiment under the base project directory:
   ```bash
   structpy create_dirs --path ./collaborative_project/experiment_01
   structpy create_dirs --path ./collaborative_project/experiment_02
   ```

3. **Validate Data for Experiment 1:**
   ```bash
   structpy validate --file ./collaborative_project/experiment_01/data.csv
   ```

   Example output:
   ```
   Warning: Missing values detected (2.5%)
   Info: No duplicate column names found.
   Warning: Outliers detected in column velocity
   Data validation complete.
   ```

4. **Generate Results Filenames:**
   Generate a unique filename for storing processed results:
   ```bash
   structpy generate_filename --prefix exp1_results --ext csv
   ```

   Output:
   ```
   Generated filename: exp1_results_20241121-154500.csv
   ```

5. **Backup the Project:**
   Backup the entire collaborative project into a timestamped archive:
   ```bash
   structpy backup --path ./collaborative_project --archive collaborative_project_backup
   ```

   Result:
   ```
   collaborative_project_backup_20241121-160000-d4e5f6.zip
   ```

---

## **Development**

### **Run Tests**
To ensure the tool is working as expected, run the test suite:
```bash
pytest tests/ -v
```

### **Contributing**
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b my-feature
   ```
3. Commit your changes and push to your branch:
   ```bash
   git commit -m "Add new feature"
   git push origin my-feature
   ```
4. Open a pull request.

---

## **Future Enhancements**
- Add support for other file formats (e.g., `.json`, `.h5`).
- Extend validation to support user-defined rules.
- Integrate with cloud storage solutions for backups.

---

## **License**
This project is licensed under the MIT License. See the `LICENSE` file for details.

