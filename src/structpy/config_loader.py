import copy
import os
import yaml

# Built-in defaults, used when no config.yaml is found
DEFAULT_CONFIG = {
    "directories": {
        "input": [],
        "output": ["plots", "tables"],
        "logs": [],
        "temp": [],
    },
    "backup": {
        "default_archive_name": "project_backup",
    },
    "filename": {
        "default_prefix": "datafile",
        "default_extension": "csv",
    },
    "validation": {
        "check_missing_values": True,
        "check_duplicate_columns": True,
        "check_outliers": True,
        "missing_value_threshold": 0.2,
    },
}

def load_config(config_path=None):
    """
    Load the configuration.

    Starts from DEFAULT_CONFIG and applies settings from config_path, or from
    config.yaml in the current directory if no path is given and one exists.
    A user's "directories" section replaces the default layout; other sections
    only override the keys they set.
    """
    config = copy.deepcopy(DEFAULT_CONFIG)

    if config_path is None:
        if not os.path.exists("config.yaml"):
            return config
        config_path = "config.yaml"

    with open(config_path, "r") as file:
        user_config = yaml.safe_load(file) or {}

    for section, values in user_config.items():
        if section != "directories" and isinstance(values, dict) and isinstance(config.get(section), dict):
            config[section].update(values)
        else:
            config[section] = values
    return config
