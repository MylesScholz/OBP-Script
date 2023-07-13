# Author: Myles Scholz
# Created on June 24, 2023
# Description: Merges formatted data (output from format_data.py)
#              with existing data of the same format

import sys
import os
import csv
import functools
import datetime


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
            base_file_path = sys.argv[i + 1].strip('"')
        elif arg == "--append":
            if i + 1 > len(sys.argv):
                print("ERROR: --append argument not set")
                exit(1)
            append_file_path = sys.argv[i + 1].strip('"')
        elif arg == "--output":
            if i + 1 > len(sys.argv):
                print("ERROR: --output argument not set")
                exit(1)
            output_file_path = sys.argv[i + 1].strip('"')

    # Check that provided file paths are CSV files
    if not base_file_path.lower().endswith(".csv"):
        print("ERROR: base file must be in .csv format")
        exit(1)

    if not append_file_path.lower().endswith(".csv"):
        print("ERROR: file to append must be in .csv format")
        exit(1)

    if not output_file_path.lower().endswith(".csv"):
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


def equal_identifiers(row1: dict, row2: dict):
    if row1["Observation No."] == row2["Observation No."]:
        return True
    elif (
        row1["Associated plant - Inaturalist URL"]
        == row2["Associated plant - Inaturalist URL"]
        and row1["Associated plant - Inaturalist URL"] != ""
        and row2["Associated plant - Inaturalist URL"] != ""
        and row1["Sample ID"] == row2["Sample ID"]
        and row1["Specimen ID"] == row2["Specimen ID"]
    ):
        return True
    elif (
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
    # Search the data linearly
    for i, entry in enumerate(data):
        # Check if all keys match
        if equal_identifiers(entry, row):
            # Return the index of the matching row
            return i

    # Set default return value to -1 (row not found in data)
    return -1


def compare_numerical_string(string1: str, string2: str):
    # Treat an empty string as the largest value
    if string1 == "" and string2 != "":
        return 1
    if string2 == "" and string1 != "":
        return -1
    if string1 == "" and string2 == "":
        return 0

    # At this point, both strings have content
    # Try converting to integers to compare
    try:
        number1 = int(string1)
        number2 = int(string2)

        return (number1 > number2) - (number1 < number2)
    except:
        # Converting to integers failed, so just compare as strings
        return (string1 > string2) - (string1 < string2)


def compare_string(string1, string2):
    # Treat an empty string as the largest value
    if string1 == "" and string2 != "":
        return 1
    if string2 == "" and string1 != "":
        return -1

    # At this point, either both are blank or both have content.
    # Either way, they can be compared directly
    return (string1 > string2) - (string1 < string2)


def compare_month(month1: str, month2: str):
    # Treat empty strings as the largest value
    if month1 == "" and month2 != "":
        return 1
    if month2 == "" and month1 != "":
        return -1
    if month1 == "" and month2 == "":
        return 0

    months = {
        "I": 1,
        "II": 2,
        "III": 3,
        "IV": 4,
        "V": 5,
        "VI": 6,
        "VII": 7,
        "VIII": 8,
        "IX": 9,
        "X": 10,
        "XI": 11,
        "XII": 12,
    }

    return (months[month1] > months[month2]) - (months[month1] < months[month2])


def compare_rows(row1: dict, row2: dict):
    # First, compare "Observation No."
    observation_no_comparison = compare_numerical_string(
        row1["Observation No."], row2["Observation No."]
    )
    if observation_no_comparison != 0:
        return observation_no_comparison

    # Second, compare "Collector - Last Name"
    last_name_comparison = compare_string(
        row1["Collector - Last Name"], row2["Collector - Last Name"]
    )
    if last_name_comparison != 0:
        return last_name_comparison

    # Third, compare "Collector - First Name"
    first_name_comparison = compare_string(
        row1["Collector - First Name"], row2["Collector - First Name"]
    )
    if first_name_comparison != 0:
        return first_name_comparison

    # Fourth, compare "Month 1"
    month_comparison = compare_month(row1["Month 1"], row2["Month 1"])
    if month_comparison != 0:
        return month_comparison

    # Fifth, compare "Collection Day 1"
    day_comparison = compare_numerical_string(
        row1["Collection Day 1"], row2["Collection Day 1"]
    )
    if day_comparison != 0:
        return day_comparison

    # Sixth, compare "Sample ID"
    sample_id_comparison = compare_numerical_string(
        row1["Sample ID"], row2["Sample ID"]
    )
    if sample_id_comparison != 0:
        return sample_id_comparison

    # Seventh, compare "Specimen ID"
    specimen_id_comparison = compare_numerical_string(
        row1["Specimen ID"], row2["Specimen ID"]
    )
    if specimen_id_comparison != 0:
        return specimen_id_comparison

    return 0


def row_is_empty(row: dict):
    for column in row:
        if row[column] != "":
            return False

    return True


def merge_files(base_file_path: str, append_file_path: str, output_file_path=""):
    """
    Merges files with formatted iNaturalist data into a single sorted and indexed data file
    Assumes base file and file to append are CSVs with the same headers

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

        # Confirm header correspondence between base and append files
        base_header = base_data[0].keys()
        append_header = append_data[0].keys()
        if any(
            [
                base_column != append_column
                for base_column, append_column in zip(base_header, append_header)
            ]
        ):
            print("ERROR: base and append file headers do not match")
            exit(1)

        # Loop through the data to append, checking for duplicates and updates
        for row in append_data:
            # Search for current row in base data (using keys)
            index = search_data_for_row(base_data, row)

            if index == -1 and row["Dec. Lat."] != "" and row["Dec. Long."] != "":
                # The current row is new; append it to the base data
                # (Exclude rows that don't have coordinates)
                base_data.append(row)
            else:
                # Fill in empty columns in the base data with values from the current row
                for column in row:
                    if (
                        column in base_header
                        and base_data[index][column] == ""
                        and row[column] != ""
                    ):
                        base_data[index][column] = row[column]

        # Sort and index the merged data (base_data)

        # Sort with a custom comparison function
        base_data.sort(key=functools.cmp_to_key(compare_rows))

        # Search through sorted data backwards to find the last observation number
        last_observation_no_string = ""
        last_observation_no_index = -1
        for i in range(len(base_data) - 1, -1, -1):
            if base_data[i]["Observation No."] != "":
                last_observation_no_string = base_data[i]["Observation No."]
                last_observation_no_index = i
                break

        if last_observation_no_string != "" and last_observation_no_string.isnumeric():
            # Convert the observation number to an integer and add one to get the next number
            last_observation_no = int(last_observation_no_string)
            next_observation_no = last_observation_no + 1
        else:
            # No previous observation number in the base data, so start at zero (plus the year prefix)
            current_year = str(datetime.datetime.now().year)[2:]
            next_observation_no = int(current_year + "00000")

        # Add observation numbers sequentially
        for i in range(last_observation_no_index + 1, len(base_data)):
            if not row_is_empty(base_data[i]):
                base_data[i]["Observation No."] = str(next_observation_no)
                next_observation_no += 1

        # Write updated base data to output file
        with open(output_file_path, "w", newline="") as output_file:
            csv_writer = csv.DictWriter(output_file, fieldnames=base_header)
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
