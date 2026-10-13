import argparse  # for command-line argument parsing
import pandas as pd
from core_features import create_project_dirs, backup_project, generate_filename
from validate import validate_data

def main():
    parser = argparse.ArgumentParser(description="StructPy: A tool for managing academic data projects.")
    parser.add_argument("action", choices=["create_dirs", "backup", "generate_filename", "validate"],
                        help="Action to perform")
    parser.add_argument("--path", help="Base path for create_dirs or backup")
    parser.add_argument("--archive", help="Archive name for backup")
    parser.add_argument("--prefix", help="Prefix for filename generation")
    parser.add_argument("--ext", help="Extension for filename generation")
    parser.add_argument("--file", help="Path to CSV file for validation")

    args = parser.parse_args()

    if args.action == "create_dirs":
        if not args.path:
            print("Error: --path is required for create_dirs")
        else:
            create_project_dirs(args.path)
            print(f"Directories created successfully at {args.path}.")
    elif args.action == "backup":
        if not args.path:
            print("Error: --path is required for backup")
        else:
            backup_project(args.path, args.archive)
    elif args.action == "generate_filename":
        prefix = args.prefix or "file"
        ext = args.ext or "txt"
        filename = generate_filename(prefix, ext)
        print(f"Generated filename: {filename}")
    elif args.action == "validate":
        if not args.file:
            print("Error: --file is required for validation")
        else:
            df = pd.read_csv(args.file)
            validate_data(df)

if __name__ == "__main__":
    main()
