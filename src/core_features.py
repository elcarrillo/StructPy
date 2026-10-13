import os
import re
import zipfile
from datetime import datetime
import uuid
import time
from config_loader import load_config

# Archives made by backup_project: <name>_YYYYMMDD-HHMMSS-<6 hex>.zip
BACKUP_NAME = re.compile(r"_\d{8}-\d{6}-[0-9a-f]{6}\.zip$")

# Core Feature 1: Directory Setup
def create_project_dirs(base_path):
    """Creates a directory structure based on YAML configuration."""
    structure = load_config()["directories"]
    for folder, subfolders in structure.items():
        os.makedirs(os.path.join(base_path, folder), exist_ok=True)
        for sub in subfolders:
            os.makedirs(os.path.join(base_path, folder, sub), exist_ok=True)
    print(f"Project directories created at {base_path}")

# Core Feature 2: Backup Utility
def backup_project(base_path, archive_name=None):
    """
    Compresses the project directory into a timestamped zip file.

    "results" or "results.zip" both become results_<timestamp>-<id>.zip,
    so earlier backups are never overwritten. Returns the archive path.
    """
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
    prefix = prefix or "_"
    ext = ext or "txt"
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    unique_id = uuid.uuid4().hex[:6]  # Generate 6-character unique ID
    return f"{prefix}_{timestamp}-{unique_id}.{ext}"
