import argparse  # for command-line argument parsing
import json
import os
import sys
from core_features import create_project_dirs, backup_project, generate_filename
from validate import validate_file, summarize

def main():
    parser = argparse.ArgumentParser(description="StructPy: A tool for managing academic data projects.")
    parser.add_argument("action", choices=["create_dirs", "backup", "generate_filename", "validate"],
                        help="Action to perform")
    parser.add_argument("--path", help="Base path for create_dirs or backup")
    parser.add_argument("--archive", help="Archive name for backup")
    parser.add_argument("--prefix", help="Prefix for filename generation")
    parser.add_argument("--ext", help="Extension for filename generation")
    parser.add_argument("--file", help="Path to CSV file for validation")
    parser.add_argument("--json", action="store_true", help="Output validation results as JSON")

    args = parser.parse_args()
    if args.json and args.action != "validate":
        parser.error("--json is only supported for validate")

    # parser.error prints the usage and exits with status 2
    if args.action == "create_dirs":
        if not args.path:
            parser.error("--path is required for create_dirs")
        try:
            create_project_dirs(args.path)
        except (OSError, ValueError) as error:
            parser.error(str(error))
        print(f"Directories created successfully at {args.path}.")
    elif args.action == "backup":
        if not args.path:
            parser.error("--path is required for backup")
        try:
            backup_project(args.path, args.archive)
        except (OSError, ValueError) as error:
            parser.error(str(error))
    elif args.action == "generate_filename":
        filename = generate_filename(args.prefix, args.ext)
        print(f"Generated filename: {filename}")
    elif args.action == "validate":
        if not args.file:
            parser.error("--file is required for validation")
        if not os.path.isfile(args.file):
            parser.error(f"file not found: {args.file}")
        results = validate_file(args.file)
        print(json.dumps(results) if args.json else summarize(results, args.file))
        sys.exit(0 if results["passed"] else 1)

if __name__ == "__main__":
    main()
