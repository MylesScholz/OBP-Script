# Author: Myles Scholz
# Created on June 24, 2023
# Description: Merges formatted data (output from format_data.py)
#              with existing data of the same format

import sys
import os


def parse_command_line():
    """
    Parses command line arguments, checking for --base, --append, and --output values
    """

    base_file_path = ""
    append_file_path = ""
    output_file_path = ""

    # Check for --base and --append (required)
    if "--base" not in sys.argv:
        print("ERROR: --base argument not set")
        exit(1)

    if "--append" not in sys.argv:
        print("ERROR: --append argument not set")
        exit(1)

    # Parse command line arguments
    for i, arg in enumerate(sys.argv):
        if arg == "--base":
            if i + 1 > len(sys.argv):
                print("ERROR: --base argument not set")
                exit(1)
            base_file_path = sys.argv[i + 1]
        elif arg == "--append":
            if i + 1 > len(sys.argv):
                print("ERROR: --append argument not set")
                exit(1)
            append_file_path = sys.argv[i + 1]
        elif arg == "--output":
            if i + 1 > len(sys.argv):
                print("ERROR: --output argument not set")
                exit(1)
            output_file_path = sys.argv[i + 1]

    # Check that provided file paths are CSV files
    if not base_file_path.endswith(".csv"):
        print("ERROR: base file must be in .csv format")
        exit(1)

    if not append_file_path.endswith(".csv"):
        print("ERROR: file to append must be in .csv format")
        exit(1)

    if not output_file_path.endswith(".csv"):
        print("ERROR: output file must be in .csv format")
        exit(1)

    # Check that base and append files exist
    if not os.path.isfile(base_file_path):
        print("ERROR: base file must exist")
        exit(1)

    if not os.path.isfile(append_file_path):
        print("ERROR: file to append must exist")
        exit(1)

    return base_file_path, append_file_path, output_file_path


def merge_files(base_file_path: str, append_file_path: str, output_file_path: str):
    """
    Merges files with formatted iNaturalist data into a single sorted and indexed data file

    Assumes the provided files are sorted by date and time of observation (results of format_data.py should be)
    """

    if (
        base_file_path is None
        or base_file_path == ""
        or append_file_path is None
        or append_file_path == ""
    ):
        print("ERROR: base file or file to append not provided")
        exit(1)

    # If no output file is specified, modify the base file
    if output_file_path == "":
        output_file_path = base_file_path

    # TODO: merging

    return output_file_path


def main():
    base_file_path, append_file_path, output_file_path = parse_command_line()
    output_file_path = merge_files(base_file_path, append_file_path, output_file_path)


if __name__ == "__main__":
    main()
