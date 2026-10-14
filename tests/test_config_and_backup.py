import os
import sys
import zipfile
import pytest

from config_loader import load_config, DEFAULT_CONFIG
from core_features import create_project_dirs, backup_project
import main

# --- Config loading ---

def test_load_config_without_config_file(tmp_path, monkeypatch):
    """With no config.yaml in the current folder, the built-in defaults are used."""
    monkeypatch.chdir(tmp_path)
    assert load_config() == DEFAULT_CONFIG

def test_load_config_from_current_folder(tmp_path, monkeypatch):
    """A config.yaml in the current folder overrides the defaults."""
    (tmp_path / "config.yaml").write_text(
        "directories:\n"
        "  raw: []\n"
        "  figures: [draft]\n"
        "validation:\n"
        "  missing_value_threshold: 0.5\n"
    )
    monkeypatch.chdir(tmp_path)
    config = load_config()

    # directories are replaced, not merged with the default layout
    assert config["directories"] == {"raw": [], "figures": ["draft"]}
    # other sections keep the defaults they don't override
    assert config["validation"]["missing_value_threshold"] == 0.5
    assert config["validation"]["check_outliers"] is True
    assert config["backup"] == DEFAULT_CONFIG["backup"]

def test_load_config_empty_file(tmp_path, monkeypatch):
    """An empty config.yaml falls back to the defaults."""
    (tmp_path / "config.yaml").write_text("")
    monkeypatch.chdir(tmp_path)
    assert load_config() == DEFAULT_CONFIG

def test_load_config_missing_explicit_path(tmp_path):
    """Asking for a config file that doesn't exist is an error."""
    with pytest.raises(FileNotFoundError):
        load_config(str(tmp_path / "nope.yaml"))

def test_create_project_dirs_uses_project_config(tmp_path, monkeypatch):
    """create_dirs follows the config.yaml of the folder it is run from."""
    (tmp_path / "config.yaml").write_text("directories:\n  raw: []\n  figures: [draft]\n")
    monkeypatch.chdir(tmp_path)
    create_project_dirs("proj")

    assert sorted(os.listdir(tmp_path / "proj")) == ["figures", "raw"]
    assert (tmp_path / "proj" / "figures" / "draft").is_dir()

# --- Command line, run from a folder without config.yaml ---

def run_cli(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["structpy", *args])
    main.main()

def test_cli_help_outside_repo(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc:
        run_cli(monkeypatch, "--help")
    assert exc.value.code == 0
    assert "StructPy" in capsys.readouterr().out

def test_cli_create_dirs_outside_repo(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_cli(monkeypatch, "create_dirs", "--path", "proj")
    for folder in DEFAULT_CONFIG["directories"]:
        assert (tmp_path / "proj" / folder).is_dir()

def test_cli_backup_default_name(tmp_path, monkeypatch):
    """Without --archive, the backup uses the configured name and a single .zip."""
    (tmp_path / "proj").mkdir()
    (tmp_path / "proj" / "data.csv").write_text("a,b\n1,2\n")
    monkeypatch.chdir(tmp_path)
    run_cli(monkeypatch, "backup", "--path", "proj")

    zips = list(tmp_path.glob("*.zip"))
    assert len(zips) == 1
    assert zips[0].name.startswith("project_backup_")
    assert not zips[0].name.endswith(".zip.zip")

# --- Backups ---

@pytest.fixture
def project(tmp_path):
    proj = tmp_path / "proj"
    (proj / "input").mkdir(parents=True)
    (proj / "input" / "data.csv").write_text("a,b\n1,2\n")
    return proj

@pytest.mark.parametrize("name", ["results", "results.zip"])
def test_backup_name(project, tmp_path, name):
    """Names with or without .zip give results_<timestamp>-<id>.zip."""
    archive = backup_project(str(project), str(tmp_path / name))

    assert os.path.exists(archive)
    filename = os.path.basename(archive)
    assert filename.startswith("results_")
    assert filename.endswith(".zip")
    assert not filename.endswith(".zip.zip")

def test_backup_contents(project, tmp_path):
    archive = backup_project(str(project), str(tmp_path / "results"))
    with zipfile.ZipFile(archive) as zf:
        assert "input/data.csv" in zf.namelist()

def test_backup_keeps_empty_folders(project, tmp_path):
    (project / "logs").mkdir()
    archive = backup_project(str(project), str(tmp_path / "results"))
    with zipfile.ZipFile(archive) as zf:
        assert "logs/" in zf.namelist()

def test_backup_from_inside_project(project, monkeypatch):
    """Backing up the current folder skips earlier backups and the new archive,
    but keeps other zip files such as zipped data."""
    (project / "input" / "raw_data.zip").write_bytes(b"not really a zip")
    monkeypatch.chdir(project)

    first = backup_project(".")
    second = backup_project(".")

    with zipfile.ZipFile(first) as zf:
        assert sorted(n for n in zf.namelist() if not n.endswith("/")) == [
            "input/data.csv", "input/raw_data.zip"]
    with zipfile.ZipFile(second) as zf:
        names = zf.namelist()
        assert os.path.basename(first) not in names
        assert os.path.basename(second) not in names
        assert "input/raw_data.zip" in names

def test_backup_does_not_overwrite(project, tmp_path):
    """Two backups with the same name (even within one second) are both kept."""
    first = backup_project(str(project), str(tmp_path / "results"))
    second = backup_project(str(project), str(tmp_path / "results"))

    assert first != second
    assert os.path.exists(first) and os.path.exists(second)

@pytest.mark.parametrize("source_kind", ["missing", "file"])
def test_backup_rejects_invalid_source(tmp_path, source_kind):
    source = tmp_path / "source"
    if source_kind == "file":
        source.write_text("data")
    with pytest.raises((FileNotFoundError, NotADirectoryError)):
        backup_project(source, str(tmp_path / "results"))
    assert not list(tmp_path.glob("*.zip"))

@pytest.mark.parametrize("source_kind", ["missing", "file"])
def test_cli_backup_rejects_invalid_source(tmp_path, monkeypatch, capsys, source_kind):
    monkeypatch.chdir(tmp_path)
    if source_kind == "file":
        (tmp_path / "source").write_text("data")
    with pytest.raises(SystemExit) as exc:
        run_cli(monkeypatch, "backup", "--path", "source")
    assert exc.value.code == 2
    error = capsys.readouterr().err
    assert "Backup source" in error
    assert "Traceback" not in error
    assert not list(tmp_path.glob("*.zip"))

@pytest.mark.parametrize("level", ["folder", "subfolder"])
@pytest.mark.parametrize("path_kind", ["parent", "absolute"])
def test_create_dirs_rejects_escaping_paths(tmp_path, monkeypatch, level, path_kind):
    import yaml

    outside = tmp_path / "outside"
    bad_path = "../outside" if path_kind == "parent" else str(outside)
    structure = {"safe": []}
    if level == "folder":
        structure[bad_path] = []
    else:
        structure["nested"] = [bad_path]
    (tmp_path / "config.yaml").write_text(yaml.safe_dump({"directories": structure}))
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="inside the project"):
        create_project_dirs("project")
    assert not (tmp_path / "project").exists()
    assert not outside.exists()

def test_create_dirs_rejects_symlink_escape(tmp_path, monkeypatch):
    outside = tmp_path / "outside"
    outside.mkdir()
    project = tmp_path / "project"
    project.mkdir()
    (project / "linked").symlink_to(outside, target_is_directory=True)
    (tmp_path / "config.yaml").write_text("directories:\n  safe: []\n  linked: [child]\n")
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="inside the project"):
        create_project_dirs(project)
    assert not (outside / "child").exists()
    assert not (project / "safe").exists()

def test_create_dirs_allows_nested_paths(tmp_path, monkeypatch):
    (tmp_path / "config.yaml").write_text("directories:\n  data/raw: [measurements/daily]\n")
    monkeypatch.chdir(tmp_path)
    create_project_dirs("project")
    assert (tmp_path / "project/data/raw/measurements/daily").is_dir()

def test_cli_create_dirs_rejects_escape(tmp_path, monkeypatch, capsys):
    (tmp_path / "config.yaml").write_text("directories:\n  ../outside: []\n")
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc:
        run_cli(monkeypatch, "create_dirs", "--path", "project")
    assert exc.value.code == 2
    assert "inside the project" in capsys.readouterr().err
    assert not (tmp_path / "outside").exists()

@pytest.mark.parametrize("options,prefix,extension", [
    ([], "custom", "csv"),
    (["--prefix", "override"], "override", "csv"),
    (["--ext", "tsv"], "custom", "tsv"),
])
def test_cli_filename_uses_config(tmp_path, monkeypatch, capsys, options, prefix, extension):
    (tmp_path / "config.yaml").write_text(
        "filename:\n  default_prefix: custom\n  default_extension: csv\n"
    )
    monkeypatch.chdir(tmp_path)
    run_cli(monkeypatch, "generate_filename", *options)
    output = capsys.readouterr().out.strip()
    assert output.startswith(f"Generated filename: {prefix}_")
    assert output.endswith(f".{extension}")

def test_cli_filename_uses_builtin_defaults(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    run_cli(monkeypatch, "generate_filename")
    output = capsys.readouterr().out.strip()
    assert output.startswith("Generated filename: datafile_")
    assert output.endswith(".csv")
