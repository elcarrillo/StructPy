import os
import re
import zipfile
from datetime import datetime
from pathlib import Path
import uuid
import time
from config_loader import load_config

# Archives made by backup_project: <name>_YYYYMMDD-HHMMSS-<6 hex>.zip
BACKUP_NAME = re.compile(r"_\d{8}-\d{6}-[0-9a-f]{6}\.zip$")

# Core Feature 1: Directory Setup
def create_project_dirs(base_path):
    """Creates a directory structure based on YAML configuration."""
    structure = load_config()["directories"]
    base = Path(base_path).resolve()
    paths = []

    def project_path(*parts):
        for part in parts:
            if Path(part).is_absolute() or ".." in Path(part).parts:
                raise ValueError(f"Directory must stay inside the project: {part}")
        path = base.joinpath(*parts).resolve()
        if base != path and base not in path.parents:
            raise ValueError(f"Directory must stay inside the project: {path}")
        return path

    # Check the entire layout before creating any directories.
    for folder, subfolders in structure.items():
        paths.append(project_path(folder))
        for sub in subfolders:
            paths.append(project_path(folder, sub))
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
    print(f"Project directories created at {base_path}")

# Core Feature 2: Backup Utility
def backup_project(base_path, archive_name=None):
    """
    Compresses the project directory into a timestamped zip file.

    "results" or "results.zip" both become results_<timestamp>-<id>.zip,
    so earlier backups are never overwritten. Returns the archive path.
    """
    if not os.path.exists(base_path):
        raise FileNotFoundError(f"Backup source not found: {base_path}")
    if not os.path.isdir(base_path):
        raise NotADirectoryError(f"Backup source is not a directory: {base_path}")
    archive_name = archive_name or load_config()["backup"]["default_archive_name"]
    if archive_name.endswith(".zip"):
        archive_name = archive_name[:-len(".zip")]
    archive_path = os.path.abspath(generate_filename(archive_name, "zip"))

    # Skip earlier StructPy backups (and this archive) so that backing up a
    # folder that holds its own backups doesn't nest them inside each other
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(base_path):
            dirs.sort()
            for d in dirs:
                path = os.path.join(root, d)
                zf.write(path, os.path.relpath(path, base_path))  # keeps empty folders
            for name in sorted(files):
                path = os.path.join(root, name)
                if BACKUP_NAME.search(name) or os.path.abspath(path) == archive_path:
                    continue
                zf.write(path, os.path.relpath(path, base_path))

    print(f"Project backed up as {archive_path}")
    return archive_path

def generate_filename(prefix=None, ext=None):
    """Generates a unique filename."""
    if prefix is None or ext is None:
        config = load_config()["filename"]
        prefix = config["default_prefix"] if prefix is None else prefix
        ext = config["default_extension"] if ext is None else ext
    prefix = prefix or "_"
    ext = ext or "txt"
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    unique_id = uuid.uuid4().hex[:6]  # Generate 6-character unique ID
    return f"{prefix}_{timestamp}-{unique_id}.{ext}"
