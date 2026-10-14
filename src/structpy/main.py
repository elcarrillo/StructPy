import argparse  # for command-line argument parsing
import json
import logging
import os
import sys
from .config_loader import load_config
from .core_features import create_project_dirs, backup_project, generate_filename
from .validate import validate_file, summarize

def build_parser():
    # Options every command accepts
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--config",
                        help="Path to a config YAML file (default: config.yaml in the current folder, if present)")

    parser = argparse.ArgumentParser(prog="structpy",
                                     description="StructPy: A tool for managing academic data projects.")
    commands = parser.add_subparsers(dest="action", required=True, metavar="command")

    p = commands.add_parser("create_dirs", parents=[common], help="Create the project folder structure")
    p.add_argument("--path", required=True, help="Base path for the project")

    p = commands.add_parser("backup", parents=[common], help="Zip a project folder into a timestamped archive")
    p.add_argument("--path", required=True, help="Project folder to back up")
    p.add_argument("--archive", help="Archive name (default: from config)")

    p = commands.add_parser("generate_filename", parents=[common], help="Print a unique, timestamped filename")
    p.add_argument("--prefix", help="Filename prefix (default: from config)")
    p.add_argument("--ext", help="File extension (default: from config)")

    p = commands.add_parser("validate", parents=[common],
                            help="Check a CSV file for missing values, duplicate columns and outliers")
    p.add_argument("--file", required=True, help="Path to the CSV file")
    p.add_argument("--json", action="store_true", help="Output validation results as JSON")

    return parser

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # parser.error prints the usage and exits with status 2
    if args.config and not os.path.isfile(args.config):
        parser.error(f"config file not found: {args.config}")
    config = load_config(args.config)

    if args.action == "create_dirs":
        try:
            create_project_dirs(args.path, config)
        except (OSError, ValueError) as error:
            parser.error(str(error))
        print(f"Directories created successfully at {args.path}.")
    elif args.action == "backup":
        try:
            backup_project(args.path, args.archive, config)
        except (OSError, ValueError) as error:
            parser.error(str(error))
    elif args.action == "generate_filename":
        prefix = config["filename"]["default_prefix"] if args.prefix is None else args.prefix
        ext = config["filename"]["default_extension"] if args.ext is None else args.ext
        filename = generate_filename(prefix, ext)
        print(f"Generated filename: {filename}")
    elif args.action == "validate":
        if not os.path.isfile(args.file):
            parser.error(f"file not found: {args.file}")
        results = validate_file(args.file, config)
        print(json.dumps(results) if args.json else summarize(results, args.file))
        sys.exit(0 if results["passed"] else 1)

if __name__ == "__main__":
    main()
