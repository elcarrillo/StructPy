# **StructPy**

StructPy is a Python-based command-line tool designed for academics and scientists to manage data projects effectively. It simplifies workflows by creating structured project directories, generating timestamped filenames, validating datasets, and backing up projects seamlessly.

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
├── src/                     # Source code for the tool
│   ├── __init__.py          # Marks the 'src' folder as a package
│   ├── core_features.py     # Core functionality for directories, backups, and filenames
│   ├── validate.py          # Validation logic for datasets
├── main.py                  # Main script for the CLI
├── config.yaml              # Configuration file for customizing behavior
├── requirements.txt         # Project dependencies
├── setup.py                 # Installation script
├── README.md                # Project documentation
├── LICENSE                  # License for the project
├── tests/                   # Unit tests
│   ├── __init__.py          # Optional, for Python <3.3
│   ├── test_core_features.py # Tests for core features
│   ├── test_validate.py     # Tests for validation logic
```

---

## **Configuration**

Customize the tool's behavior using the `config.yaml` file in the project root.

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

Run the tool using the command-line interface via the `structpy` command. Below are examples of typical workflows:

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

### **2. Generate Filenames**
```bash
structpy generate_filename --prefix results --ext csv
```

**Output:**
```
Generated filename: results_20241121-153200.csv
```

You can customize the prefix and extension using the command-line arguments or rely on defaults from `config.yaml`.

---

### **3. Validate a Dataset**
```bash
structpy validate --file data.csv
```

**Example Output:**
```
Info: Missing values detected (5.0%)
Warning: Duplicate column names found
Warning: Outliers detected in column temperature
Data validation complete.
```

---

### **4. Backup a Project**
```bash
structpy backup --path ./experiment_001 --archive experiment_backup --backup-path ./backups
```

**Result:**
The project is compressed into `./backups/experiment_backup.zip`.

---

## **Sample Workflow**

### **Scenario**: Preparing and managing a new experimental project.

1. **Create a project directory:**
   ```bash
   structpy create_dirs --path ./experiment_001
   ```

2. **Process and validate your data:**
   ```bash
   structpy validate --file raw_data.csv
   ```

3. **Generate filenames for processed datasets:**
   ```bash
   structpy generate_filename --prefix processed_data --ext csv
   ```

4. **Store and back up the project:**
   ```bash
   structpy backup --path ./experiment_001 --archive experiment_backup --backup-path ./backups
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

---