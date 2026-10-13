import csv
import pandas as pd
import logging
from config_loader import load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_data(df, columns=None):
    """
    Validates a DataFrame based on configuration settings.

    - Checks each column for missing values against the threshold.
    - Checks for duplicate columns.
    - Detects outliers in numeric columns (reported, but not a failure).
    - Logs warnings and errors based on thresholds.
    - Returns a summary of validation results; "passed" is False if the data
      is empty, a column has too many missing values, or column names repeat.

    columns: the column names as written in the file, if known. pandas renames
    repeated CSV headers (A, A -> A, A.1), so validate_file passes the raw
    header to catch them.
    """
    # Load validation settings from YAML configuration
    config = load_config() or {}
    validation_config = config.get("validation", {})

    # Validation results
    results = {
        "passed": True,
        "empty": False,
        "missing_values": False,
        "missing_columns": {},   # column -> fraction missing, for columns over the threshold
        "duplicate_columns": False,
        "duplicate_names": [],
        "outliers": []
    }

    # Check if DataFrame is empty
    if df.empty:
        logger.warning("The DataFrame is empty. Validation skipped.")
        results["empty"] = True
        results["passed"] = False
        return results

    # Check for missing values, per column so one empty column isn't averaged away
    if validation_config.get("check_missing_values", False):
        missing = df.isnull().mean()
        threshold = validation_config.get("missing_value_threshold", 0.1)
        over = missing[missing > threshold]
        if not over.empty:
            details = ", ".join(f"'{col}' ({frac:.0%})" for col, frac in over.items())
            logger.warning(f"Missing values exceed threshold ({threshold:.0%}) in: {details}")
            results["missing_values"] = True
            results["missing_columns"] = {col: float(frac) for col, frac in over.items()}
        elif missing.any():
            logger.info(f"Missing values detected ({df.isnull().mean().mean():.2%} overall)")

    # Check for duplicate columns
    if validation_config.get("check_duplicate_columns", False):
        names = list(columns) if columns is not None else list(df.columns)
        duplicates = list(dict.fromkeys(n for n in names if names.count(n) > 1))
        if duplicates:
            logger.error(f"Duplicate column names found: {', '.join(map(str, duplicates))}")
            results["duplicate_columns"] = True
            results["duplicate_names"] = duplicates

    # Check for outliers
    if validation_config.get("check_outliers", False):
        for column in df.select_dtypes(include=['number']).columns:
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
            if not outliers.empty:
                logger.warning(f"Outliers detected in column '{column}'")
                results["outliers"].append(column)

    results["passed"] = not (results["missing_values"] or results["duplicate_columns"])
    logger.info("Data validation complete.")
    return results

def validate_file(path):
    """Validates a CSV file, checking for duplicate names in its raw header row."""
    with open(path, newline="", encoding="utf-8-sig") as file:
        header = next(csv.reader(file), [])
    if not header:
        return validate_data(pd.DataFrame())
    return validate_data(pd.read_csv(path), columns=header)

def summarize(results, name="data"):
    """Returns a short, human-readable pass/fail summary of validate_data results."""
    lines = [f"Validation {'PASSED' if results['passed'] else 'FAILED'}: {name}"]
    if results["empty"]:
        lines.append("  - No data rows found")
    if results["missing_columns"]:
        details = ", ".join(f"'{col}' ({frac:.0%})" for col, frac in results["missing_columns"].items())
        lines.append(f"  - Too many missing values in: {details}")
    if results["duplicate_names"]:
        lines.append(f"  - Duplicate column names: {', '.join(repr(str(n)) for n in results['duplicate_names'])}")
    if results["outliers"]:
        lines.append(f"  - Outliers (warning only) in: {', '.join(repr(str(c)) for c in results['outliers'])}")
    return "\n".join(lines)
