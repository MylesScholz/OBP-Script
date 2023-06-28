# Author: Myles Scholz
# Created on June 24, 2023
# Description: Merges formatted data (output from format_data.py)
#              with existing data of the same format

import sys
import os
import csv


FORMATTED_HEADER = [
    "Observation No.",
    "Voucher No.",
    "iNaturalist ID",
    "iNaturalist Alias",
    "Collector - First Name",
    "Collector - First Name Initial",
    "Collector - Last Name",
    "Sample ID",
    "Specimen ID",
    "Collection Day 1",
    "Month 1",
    "Year 1",
    "Time 1",
    "Collection Day 2",
    "Month 2",
    "Year 2",
    "Time 2",
    "Country",
    "State",
    "County",
    "Location",
    "Collection Site Description",
    "Abbreviated Location",
    "Dec. Lat.",
    "Dec. Long.",
    "Lat/Long Accuracy",
    "Elevation",
    "Collection method",
    "Associated plant - family",
    "Associated plant - species",
    "Associated plant - Inaturalist URL",
]


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


def compare_rows(row1: dict, row2: dict):
    if (
        row1["iNaturalist Alias"] == row2["iNaturalist Alias"]
        and row1["Sample ID"] == row2["Sample ID"]
        and row1["Specimen ID"] == row2["Specimen ID"]
        and row1["Collection Day 1"] == row2["Collection Day 1"]
        and row1["Month 1"] == row2["Month 1"]
        and row1["Year 1"] == row2["Year 1"]
    ):
        return True

    return False


def search_data_for_row(data: list, row: dict):
    # Set default return value to -1 (row not found in data)
    index = -1

    # Search the data linearly
    for i, entry in enumerate(data):
        # Check if all keys match
        if compare_rows(entry, row):
            # Record the index and break the loop
            index = i
            break

    return index


def merge_files(base_file_path: str, append_file_path: str, output_file_path=""):
    """
    Merges files with formatted iNaturalist data into a single sorted and indexed data file
    WARNING: overwrites output file
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

    try:
        # Read base data from base_file_path into memory
        with open(base_file_path, newline="") as base_file:
            base_data = list(csv.DictReader(base_file))
        # Read data to append from append_file_path into memory
        with open(append_file_path, newline="") as append_file:
            append_data = list(csv.DictReader(append_file))

        # Loop through the data to append, checking for duplicates and updates
        for row in append_data:
            # Search for current row in base data (using keys)
            index = search_data_for_row(base_data, row)

            if index == -1:
                # The current row is new; append it to the base data
                base_data.append(row)
            else:
                # Fill in empty columns in the base data with values from the current row
                for column in row:
                    if base_data[index][column] == "" and row[column] != "":
                        base_data[index][column] = row[column]

        # TODO: index data

        # Write updated base data to output file
        with open(output_file_path, "w", newline="") as output_file:
            csv_writer = csv.DictWriter(output_file, fieldnames=FORMATTED_HEADER)
            csv_writer.writeheader()
            csv_writer.writerows(base_data)
    except OSError as e:
        print("ERROR: could not open '{}'".format(e.filename))
        exit(1)

    return output_file_path


def main():
    base_file_path, append_file_path, output_file_path = parse_command_line()
    output_file_path = merge_files(base_file_path, append_file_path, output_file_path)


if __name__ == "__main__":
    main()
