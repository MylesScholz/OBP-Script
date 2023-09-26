# Author: Myles Scholz
# Created on September 15, 2023
# Description: Module that merges formatted data with the Oregon Bee Atlas database
import csv
import datetime
import functools
import os

from tqdm import tqdm


# File Name Constants
SOURCES_FILE = "config/sources.csv"
MERGE_CONFIG_FILE = "config/merge_config.csv"
LABELS_CONFIG_FILE = "config/labels_config.csv"

# Column Name Constants

# Observation Number
OBSERVATION_NUMBER = "Observation No."

# Collector
ALIAS = "iNaturalist Alias"
FIRST_NAME = "Collector - First Name"
LAST_NAME = "Collector - Last Name"

# IDs and Date
SAMPLE_ID = "Sample ID"
SPECIMEN_ID = "Specimen ID"
DAY = "Collection Day 1"
MONTH = "Month 1"
YEAR = "Year 1"

# Location
LATITUDE = "Dec. Lat."
LONGITUDE = "Dec. Long."

# URL
URL = "Associated plant - Inaturalist URL"


def get_sources():
    # Read SOURCES_FILE for the sources (iNaturalist projects) to pull data from
    with open(SOURCES_FILE, newline="") as sources_file:
        sources = list(csv.DictReader(sources_file))

    return sources


def get_merge_config():
    # Read MERGE_CONFIG_FILE to get the input and output file paths
    with open(MERGE_CONFIG_FILE, newline="") as merge_config_file:
        merge_config = list(csv.DictReader(merge_config_file))[0]

    return merge_config


def read_dataset(merge_config: dict):
    print("    Loading dataset...")

    # Read the dataset at "Input File Path" into memory
    with open(merge_config["Input File Path"], newline="") as dataset_file:
        dataset = list(csv.DictReader(dataset_file))

    return dataset


def row_is_empty(row: dict):
    # Loop through columns, checking for any non-empty strings
    for column in row:
        if row[column] != "" and row[column] is not None:
            return False

    return True


def remove_empty_rows(data: list):
    pruned_data = []

    for row in data:
        if not row_is_empty(row):
            pruned_data.append(row)

    return pruned_data


def str_to_int_catch(string: str):
    """
    Attempts to convert a string to an integer, catching errors if unsuccessful
    """

    try:
        value = int(string)
    except:
        value = string

    return value


def equal_identifiers(row1: dict, row2: dict):
    """
    A Boolean function that compares two rows of formatted data
    Returns true if there is a match of any of the following, in order:
    1. Observation No.
    2. Associated plant - Inaturalist URL, Sample ID, and Specimen ID
    3. iNaturalist Alias, Sample ID, Specimen ID, Collection Day 1, Month 1, and Year 1
    """

    obs_no_1 = str_to_int_catch(row1[OBSERVATION_NUMBER])
    obs_no_2 = str_to_int_catch(row2[OBSERVATION_NUMBER])

    sample_id_1 = str_to_int_catch(row1[SAMPLE_ID])
    sample_id_2 = str_to_int_catch(row2[SAMPLE_ID])

    specimen_id_1 = str_to_int_catch(row1[SPECIMEN_ID])
    specimen_id_2 = str_to_int_catch(row2[SPECIMEN_ID])

    day_1 = str_to_int_catch(row1[DAY])
    day_2 = str_to_int_catch(row2[DAY])

    year_1 = str_to_int_catch(row1[YEAR])
    year_2 = str_to_int_catch(row2[YEAR])

    if obs_no_1 != "" and obs_no_1 == obs_no_2:
        return True
    elif (
        row1[URL] == row2[URL]
        and row1[URL] != ""
        and sample_id_1 == sample_id_2
        and specimen_id_1 == specimen_id_2
    ):
        return True
    elif (
        row1[ALIAS] == row2[ALIAS]
        and sample_id_1 == sample_id_2
        and specimen_id_1 == specimen_id_2
        and day_1 == day_2
        and row1[MONTH] == row2[MONTH]
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
    """
    A comparison function for two strings of numbers
    """

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
    """
    A comparison function for strings
    Treats empty strings as the largest value (opposite of default str comparison)
    """

    # Treat an empty string as the largest value
    if string1 == "" and string2 != "":
        return 1
    if string2 == "" and string1 != "":
        return -1

    # At this point, either both are blank or both have content.
    # Either way, they can be compared directly
    return (string1 > string2) - (string1 < string2)


def compare_month(month1: str, month2: str):
    """
    A comparison function for formatted months (Roman numerals 1-12)
    """

    # Treat empty strings as the largest value
    if month1 == "" and month2 != "":
        return 1
    if month2 == "" and month1 != "":
        return -1
    if month1 == "" and month2 == "":
        return 0

    # Dict linking Roman numerals to decimal values
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

    # Return comparison of decimal value of given months
    return (months[month1] > months[month2]) - (months[month1] < months[month2])


def compare_rows(row1: dict, row2: dict):
    """
    Custom comparison function for sorting merged data
    """

    # First, compare "Observation No."
    observation_no_comparison = compare_numerical_string(
        row1[OBSERVATION_NUMBER], row2[OBSERVATION_NUMBER]
    )
    if observation_no_comparison != 0:
        return observation_no_comparison

    # Second, compare "Collector - Last Name"
    last_name_comparison = compare_string(row1[LAST_NAME], row2[LAST_NAME])
    if last_name_comparison != 0:
        return last_name_comparison

    # Third, compare "Collector - First Name"
    first_name_comparison = compare_string(row1[FIRST_NAME], row2[FIRST_NAME])
    if first_name_comparison != 0:
        return first_name_comparison

    # Fourth, compare "Month 1"
    month_comparison = compare_month(row1[MONTH], row2[MONTH])
    if month_comparison != 0:
        return month_comparison

    # Fifth, compare "Collection Day 1"
    day_comparison = compare_numerical_string(row1[DAY], row2[DAY])
    if day_comparison != 0:
        return day_comparison

    # Sixth, compare "Sample ID"
    sample_id_comparison = compare_numerical_string(row1[SAMPLE_ID], row2[SAMPLE_ID])
    if sample_id_comparison != 0:
        return sample_id_comparison

    # Seventh, compare "Specimen ID"
    specimen_id_comparison = compare_numerical_string(
        row1[SPECIMEN_ID], row2[SPECIMEN_ID]
    )
    if specimen_id_comparison != 0:
        return specimen_id_comparison

    return 0


def merge_data(sources: list, dataset: list, formatted_dict: dict):
    """
    Merges formatted iNaturalist data and a pre-existing dataset into a single sorted and indexed dataset
    dataset and each entry in formatted_dict must have identical headers
    """

    # formatted_dict is divided by iNaturalist source, so loop through each
    for source in sources:
        print("    Merging '{}' data with dataset...".format(source["Name"]))

        append_data = formatted_dict[source["Abbreviation"]]

        # Confirm header correspondence between base and append files
        dataset_header = dataset[0].keys()
        append_header = append_data[0].keys()
        if any(
            [
                base_column != append_column
                for base_column, append_column in zip(dataset_header, append_header)
            ]
        ):
            print("ERROR: base and append file headers do not match")
            exit(1)

        # Loop through the data to append, checking for duplicates and updates
        for row in tqdm(append_data, desc="        Entries"):
            # Search for current row in base data (using keys)
            index = search_data_for_row(dataset, row)

            if index == -1:
                # The current row is new; append it to the base data
                # (Exclude rows that don't have coordinates)
                if row[LATITUDE] != "" and row[LONGITUDE] != "":
                    dataset.append(row)
            else:
                # Fill in empty columns in the base data with values from the current row
                for column in row:
                    if (
                        column in dataset_header
                        and dataset[index][column] == ""
                        and row[column] != ""
                    ):
                        dataset[index][column] = row[column]

    return dataset


def store_new_observation_index(index: int):
    # Read the labels configuration file
    with open(LABELS_CONFIG_FILE, newline="") as labels_config_file:
        labels_config = list(csv.DictReader(labels_config_file))[0]

    # Update the "Starting Row" field with the index of the first new observation
    labels_config["Starting Row"] = index

    # Write the updated dict to the configuration file
    labels_config_header = labels_config.keys()
    with open(LABELS_CONFIG_FILE, "w", newline="") as labels_config_file:
        csv_writer = csv.DictWriter(labels_config_file, fieldnames=labels_config_header)
        csv_writer.writeheader()
        csv_writer.writerow(labels_config)


def index_data(dataset: list):
    """
    Sorts a dataset and adds observation numbers to unindexed rows
    """

    # Sort with a custom comparison function
    dataset.sort(key=functools.cmp_to_key(compare_rows))

    # Search through sorted data backwards to find the last observation number
    last_observation_no_string = ""
    last_observation_no_index = -1
    for i in range(len(dataset) - 1, -1, -1):
        if dataset[i][OBSERVATION_NUMBER] != "":
            last_observation_no_string = dataset[i][OBSERVATION_NUMBER]
            last_observation_no_index = i
            break

    # Store the index of the first new observation number (for printing labels later in the pipeline)
    store_new_observation_index(last_observation_no_index + 1)

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
            dataset[i][OBSERVATION_NUMBER] = str(next_observation_no)
            next_observation_no += 1

    return dataset


def write_dataset(merge_config: dict, merged_dataset: list):
    """
    Writes a dataset to the Output File Path specified in merge_config as a CSV file
    """

    output_file_path = os.path.relpath(merge_config["Output File Path"])
    print("    Writing merged data to '{}'...".format(output_file_path))

    dataset_header = merged_dataset[0].keys()
    with open(output_file_path, "w", newline="") as output_file:
        csv_writer = csv.DictWriter(output_file, fieldnames=dataset_header)
        csv_writer.writeheader()
        csv_writer.writerows(merged_dataset)


def run(formatted_dict: dict):
    print("Merging Data...")

    # Read the source names and ids (iNaturalist projects)
    sources = get_sources()

    # Read the input and output file paths from the merge config file
    merge_config = get_merge_config()

    # Read the dataset from its file into memory
    dataset = read_dataset(merge_config)

    # Remove empty rows, which could cause problems later, from the dataset
    pruned_dataset = remove_empty_rows(dataset)

    # Merge the dataset with the given formatted data
    merged_data = merge_data(sources, pruned_dataset, formatted_dict)

    # Sort and index the data, storing the row of the first new entry
    indexed_data = index_data(merged_data)

    # Write the merged, sorted, and indexed data into a CSV file
    write_dataset(merge_config, indexed_data)

    print("Merging Data => Done\n")

    # TODO: logging

    return indexed_data
