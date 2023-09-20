# Author: Myles Scholz
# Created on September 15, 2023
# Description: Module that merges formatted data with the Oregon Bee Atlas database
import csv
import datetime
import functools


SOURCES_FILE = "config/sources.csv"
MERGE_CONFIG_FILE = "config/merge_config.csv"


def get_sources():
    # Read SOURCES_FILE for the sources (iNaturalist projects) to pull data from
    with open(SOURCES_FILE, newline="") as sources_file:
        sources = list(csv.DictReader(sources_file))

    return sources


def get_merge_config():
    # Read merge_config.csv to get the input and output file paths
    with open(MERGE_CONFIG_FILE, newline="") as merge_config_file:
        csv_reader = csv.DictReader(merge_config_file)
        merge_config = csv_reader[0]

    return merge_config


def read_dataset(merge_config: dict):
    print("    Loading dataset...")

    # Read the dataset at "Input File Path" into memory
    with open(merge_config["Input File Path"], newline="") as dataset_file:
        dataset = list(csv.DictReader(dataset_file))

    return dataset


def str_to_int_catch(string: str):
    try:
        value = int(string)
    except:
        value = string

    return value


def equal_identifiers(row1: dict, row2: dict):
    obs_no_1 = str_to_int_catch(row1["Observation No."])
    obs_no_2 = str_to_int_catch(row2["Observation No."])

    sample_id_1 = str_to_int_catch(row1["Sample ID"])
    sample_id_2 = str_to_int_catch(row2["Sample ID"])

    specimen_id_1 = str_to_int_catch(row1["Specimen ID"])
    specimen_id_2 = str_to_int_catch(row2["Specimen ID"])

    day_1 = str_to_int_catch(row1["Collection Day 1"])
    day_2 = str_to_int_catch(row2["Collection Day 1"])

    year_1 = str_to_int_catch(row1["Year 1"])
    year_2 = str_to_int_catch(row2["Year 1"])

    if obs_no_1 != "" and obs_no_1 == obs_no_2:
        return True
    elif (
        row1["Associated plant - Inaturalist URL"]
        == row2["Associated plant - Inaturalist URL"]
        and row1["Associated plant - Inaturalist URL"] != ""
        and sample_id_1 == sample_id_2
        and specimen_id_1 == specimen_id_2
    ):
        return True
    elif (
        row1["iNaturalist Alias"] == row2["iNaturalist Alias"]
        and sample_id_1 == sample_id_2
        and specimen_id_1 == specimen_id_2
        and day_1 == day_2
        and row1["Month 1"] == row2["Month 1"]
        and year_1 == year_2
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


def merge_data(sources: list, dataset: list, formatted_dict: dict):
    for source in sources:
        print("    Merging '{}' data...".format(source["Name"]))

        append_data = formatted_dict[source["Abbreviation"]]

        # Confirm header correspondence between base and append files
        base_header = dataset[0].keys()
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
            index = search_data_for_row(dataset, row)

            if index == -1:
                # The current row is new; append it to the base data
                # (Exclude rows that don't have coordinates)
                if row["Dec. Lat."] != "" and row["Dec. Long."] != "":
                    dataset.append(row)
            else:
                # Fill in empty columns in the base data with values from the current row
                for column in row:
                    if (
                        column in base_header
                        and dataset[index][column] == ""
                        and row[column] != ""
                    ):
                        dataset[index][column] = row[column]

        # Sort and index the merged data (base_data)

        # Sort with a custom comparison function
        dataset.sort(key=functools.cmp_to_key(compare_rows))

        # Search through sorted data backwards to find the last observation number
        last_observation_no_string = ""
        last_observation_no_index = -1
        for i in range(len(dataset) - 1, -1, -1):
            if dataset[i]["Observation No."] != "":
                last_observation_no_string = dataset[i]["Observation No."]
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
        for i in range(last_observation_no_index + 1, len(dataset)):
            if not row_is_empty(dataset[i]):
                dataset[i]["Observation No."] = str(next_observation_no)
                next_observation_no += 1

    return dataset


def write_dataset(merge_config: dict, merged_dataset: list):
    pass


def run(formatted_dict: dict):
    print("Merging Data")

    sources = get_sources()

    merge_config = get_merge_config()

    dataset = read_dataset(merge_config)

    merged_data = merge_data(sources, dataset, formatted_dict)

    write_dataset(merge_config, merged_data)

    print("Merging Data => Done\n")

    # TODO: logging

    return merged_data
