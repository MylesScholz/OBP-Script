# Author: Myles Scholz
# Created on September 15, 2023
# Description: Module that merges formatted data with the Oregon Bee Atlas database
import csv
import datetime
import functools
import os
import tempfile
import hashlib
import traceback
import tkinter as tk
from tkinter import filedialog
from collections import deque
import shutil


# File I/O Constants
SOURCES_FILE = "config/sources.csv"
MERGE_CONFIG_FILE = "config/merge_config.csv"
LABELS_CONFIG_FILE = "config/labels_config.csv"
LOG_FILE = "log_file.txt"
CHUNK_SIZE = 10000
MERGE_SIZE = 2

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


def write_merge_config(merge_config):
    # Open MERGE_CONFIG_FILE to write updated input and output file paths
    merge_config_header = ["Input File Path", "Output File Path"]
    with open(MERGE_CONFIG_FILE, "w", newline="") as merge_config_file:
        csv_writer = csv.DictWriter(merge_config_file, fieldnames=merge_config_header)
        csv_writer.writeheader()
        csv_writer.writerow(merge_config)


def read_csv_chunks(file_path):
    chunk = []
    with open(file_path, newline="", encoding="utf-8", errors="replace") as file:
        reader = csv.DictReader(file)

        # Loop through the given file and yield chunks while maintaining state between calls
        for row in reader:
            chunk.append(row)
            # Yield chunk when it reaches CHUNK_SIZE
            if len(chunk) >= CHUNK_SIZE:
                yield chunk
                chunk = []
        # Yield the final partial chunk
        if chunk:
            yield chunk


def row_is_empty(row: dict):
    # Loop through columns, checking for any non-empty strings
    for column in row:
        if row[column] != "" and row[column] is not None:
            return False

    return True


def generate_key(row):
    # Choose identifying key fields based on if those values exist in the following sets:
    # 1. Associated plant - Inaturalist URL, Sample ID, and Specimen ID
    # 2. iNaturalist Alias, Sample ID, Specimen ID, Collection Day 1, Month 1, and Year 1
    key_fields = []
    if row.get(URL) and row.get(SAMPLE_ID) and row.get(SPECIMEN_ID):
        key_fields = [URL, SAMPLE_ID, SPECIMEN_ID]
    elif (
        row.get(ALIAS)
        and row.get(SAMPLE_ID)
        and row.get(SPECIMEN_ID)
        and row.get(DAY)
        and row.get(MONTH)
        and row.get(YEAR)
    ):
        key_fields = [ALIAS, SAMPLE_ID, SPECIMEN_ID, DAY, MONTH, YEAR]

    # Convert the key fields to their values (as strings)
    key_values = [str(row.get(field, "")) for field in key_fields]

    # Concatenate and encode the key values as a single identifying key
    composite_key = hashlib.sha256(",".join(key_values).encode("utf-8")).hexdigest()

    return composite_key


def sort_and_dedupe_chunk(chunk, seen_keys):
    unique_rows = []

    # Loop through the chunk and add rows with observation numbers first
    for row in chunk:
        # Skip empty rows
        if row_is_empty(row):
            continue

        # If the row has an observation number, assume it is unique, add its key to the seen_keys list, and append the row to unique_rows
        if row[OBSERVATION_NUMBER]:
            # Create a unique key field for the row
            key = generate_key(row)

            # Add the key and row
            seen_keys.add(key)
            unique_rows.append(row)

    # Loop through the chunk again, this time adding any other unique rows
    for row in chunk:
        # Skip empty rows
        if row_is_empty(row):
            continue

        # Create a unique key field for the row
        key = generate_key(row)

        # If the row's key has not yet been seen, add it to seen_keys and append the row to unique_rows
        if key not in seen_keys:
            seen_keys.add(key)
            unique_rows.append(row)

    return sorted(unique_rows, key=functools.cmp_to_key(compare_rows))


def write_chunk_to_temp(chunk, fieldnames, temp_files):
    # Create a temporary file to output to
    fd, path = tempfile.mkstemp(suffix=".csv", dir="./temp")
    temp_files.append(path)

    # Write the given chunk to the temporary file and add it to the list of current temporary files
    with os.fdopen(
        fd, "w", newline="", encoding="utf-8", errors="replace"
    ) as temp_file:
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(chunk)

    return path


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


def merge_files_batch(input_files, output_file, sort_key, fieldnames):
    """
    Merges a batch of data files into a single sorted file
    """

    # A list of open file readers
    readers = []
    # A list of rows to be merged
    current_rows = []

    # Read each input file
    for file_name in input_files:
        file = open(file_name, "r", newline="", encoding="utf-8", errors="replace")
        reader = csv.DictReader(file)
        readers.append((file, reader))

        # Read the first row; input files should be sorted so the first row has the minimum sorting value
        try:
            row = next(reader)
            current_rows.append((sort_key(row), row, reader))
        except StopIteration:
            current_rows.append((None, None, reader))

    # Open the output file and write the header
    with open(
        output_file, "w", newline="", encoding="utf-8", errors="replace"
    ) as out_file:
        writer = csv.DictWriter(out_file, fieldnames=fieldnames)
        writer.writeheader()

        # Write the row with the minimum sorting value to the output until there are no valid rows left
        while True:
            # Filter for non-empty rows
            valid_rows = [
                (key, row, i)
                for i, (key, row, _) in enumerate(current_rows)
                if row is not None
            ]
            if not valid_rows:
                break

            # Write the row with the minimum sorting value
            min_key, min_row, min_idx = min(valid_rows)
            writer.writerow(min_row)

            # Read the next row from the file that the minimum row came from
            try:
                # current_rows[min_idx][2] is the reader for the file
                next_row = next(current_rows[min_idx][2])
                # Replace the minimum row with the next row
                current_rows[min_idx] = (
                    sort_key(next_row),
                    next_row,
                    current_rows[min_idx][2],
                )
            except StopIteration:
                current_rows[min_idx] = (None, None, current_rows[min_idx][2])

    # Close the readers
    for file, _ in readers:
        file.close()


def merge_sorted_files(temp_files, output_file_path, sort_key, fieldnames):
    """
    Merges a set of pre-sorted and deduped temporary data files into a single sorted dataset
    """

    if not temp_files:
        return

    # Create a queue of files to merge, starting with the temporary files created for each data chunk
    files_queue = deque(temp_files)

    # Merge files until there is one file left (the output file)
    while len(files_queue) > 1:
        print("    Merge queue:" + (" X" * len(files_queue)))

        # Create a batch of files to merge together from the files queue
        batch = []
        for _ in range(min(MERGE_SIZE, len(files_queue))):
            batch.append(files_queue.popleft())

        # If this is the final merge and all files are in the batch, merge directly into the output file
        if not files_queue and len(batch) == len(temp_files):
            merge_files_batch(batch, output_file_path, sort_key, fieldnames)
        else:
            # Create a temporary file to merge into
            fd, merged_path = tempfile.mkstemp(suffix=".csv", dir="./temp")
            os.close(fd)

            # Merge into the temporary file
            merge_files_batch(batch, merged_path, sort_key, fieldnames)

            # Add the merged file to the queue and the listing of all temporary files
            files_queue.append(merged_path)
            temp_files.append(merged_path)

        # Clean up files that were used in the merge
        for file_name in batch:
            os.remove(file_name)
            temp_files.remove(file_name)


def find_last_observation_number(file_path):
    last_observation_no = None
    last_observation_no_index = -1

    # Search through the given file row-by-row for the largest observation number
    with open(file_path, "r", newline="", encoding="utf-8", errors="replace") as file:
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            if row.get(OBSERVATION_NUMBER):
                try:
                    current_observation_no = int(row[OBSERVATION_NUMBER])
                    if (
                        last_observation_no is None
                        or current_observation_no > last_observation_no
                    ):
                        last_observation_no = current_observation_no
                        last_observation_no_index = i
                except (ValueError, TypeError):
                    continue

    # Return the observation number and its index
    return (last_observation_no, last_observation_no_index)


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


def index_data(file_path):
    """
    Adds observation numbers to unindexed rows of a sorted dataset file
    """

    # Search through sorted data to find the last observation number
    last_observation_no, last_observation_no_index = find_last_observation_number(
        file_path
    )

    # Store the index of the first new observation number (for printing labels later in the pipeline)
    store_new_observation_index(last_observation_no_index + 1)

    if last_observation_no is not None:
        # Add one to the last observation number to get the next one
        next_observation_no = last_observation_no + 1
    else:
        # No previous observation number in the base data, so start at zero (plus the year prefix)
        current_year = str(datetime.datetime.now().year)[2:]
        next_observation_no = int(current_year + "00000")

    # Create temporary output file
    temp_fd, temp_path = tempfile.mkstemp(suffix=".csv", dir="./temp")
    os.close(temp_fd)

    # Read through the input file and fill in empty observation number fields in the output
    try:
        with open(
            file_path, "r", newline="", encoding="utf-8", errors="replace"
        ) as infile, open(
            temp_path, "w", newline="", encoding="utf-8", errors="replace"
        ) as outfile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames

            # Ensure there is an observation number field in the output even if it is absent in the input
            if OBSERVATION_NUMBER not in fieldnames:
                fieldnames = fieldnames + [OBSERVATION_NUMBER]

            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            # Fill in empty observation numbers sequentially
            for row in reader:
                if not row.get(OBSERVATION_NUMBER):
                    row[OBSERVATION_NUMBER] = str(next_observation_no)
                    next_observation_no += 1

                writer.writerow(row)

        # Overwrite the input file with the indexed output
        shutil.move(temp_path, file_path)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e


def run(formatted_dict: dict):
    try:
        print("Merging Data...")

        # Read the source names and ids (iNaturalist projects)
        sources = get_sources()

        # Read the input and output file paths from the merge config file
        merge_config = get_merge_config()
        input_file_path = os.path.relpath(merge_config["Input File Path"])
        output_file_path = os.path.relpath(merge_config["Output File Path"])

        root = tk.Tk()
        root.attributes("-alpha", 0.0)
        root.attributes("-topmost", True)

        # Prompt the user with a file select dialog if specified
        if input_file_path.lower() == "select":
            input_file_path = filedialog.askopenfilename(
                initialdir="../", filetypes=[("CSV Files", "*.csv")], parent=root
            )
            merge_config["Input File Path"] = os.path.relpath(input_file_path)
            write_merge_config(merge_config)

        if output_file_path.lower() == "select":
            output_file_path = filedialog.asksaveasfilename(
                initialdir="../", filetypes=[("CSV Files", "*.csv")], parent=root
            )
            merge_config["Output File Path"] = os.path.relpath(output_file_path)
            write_merge_config(merge_config)

        root.destroy()

        # Combine the given formatted data across all sources
        new_data = []
        for source in sources:
            new_data.extend(formatted_dict[source["Abbreviation"]])

        # Read just the field names from the input file
        with open(
            input_file_path, newline="", encoding="utf-8", errors="replace"
        ) as dataset_file:
            reader = csv.DictReader(dataset_file)
            fieldnames = reader.fieldnames

        # Create a directory for temporary files if it does not exist
        if not os.path.exists("./temp"):
            os.mkdir("./temp")

        # A set of unique row keys that have been discovered so far
        seen_keys = set()
        # A list of file paths of temporary files
        temp_files = []

        # Read the dataset from its file in chunks; sort, deduplicate, and write each chunk to a temporary file
        for chunk in read_csv_chunks(input_file_path):
            # Append new data to the first chunk
            if new_data:
                chunk.extend(new_data)
                new_data = None

            sorted_chunk = sort_and_dedupe_chunk(chunk, seen_keys)
            if sorted_chunk:
                write_chunk_to_temp(sorted_chunk, fieldnames, temp_files)

        # If there was no data in the input file, process the new data as a chunk
        if new_data:
            sorted_chunk = sort_and_dedupe_chunk(new_data, seen_keys)
            if sorted_chunk:
                write_chunk_to_temp(sorted_chunk, fieldnames, temp_files)

        # Merge sorted temporary files in batches of MERGE_SIZE
        merge_sorted_files(
            temp_files, output_file_path, functools.cmp_to_key(compare_rows), fieldnames
        )

        # Index the data, storing the row of the first new entry
        index_data(output_file_path)

        print("Merging Data => Done\n")

        # Log a success
        current_date = datetime.datetime.now()
        date_str = current_date.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as log_file:
            log_file.write(
                "{}: SUCCESS - Merged new data with '{}' into '{}'\n".format(
                    date_str,
                    input_file_path,
                    output_file_path,
                )
            )
            log_file.write("\n")

        return output_file_path

    except Exception:
        # Log the error
        current_date = datetime.datetime.now()
        date_str = current_date.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as log_file:
            log_file.write("{}: ERROR while merging data:\n".format(date_str))
            log_file.write(traceback.format_exc())
            log_file.write("\n")

        input(
            "An error occurred while merging data. Check {} for details.".format(
                LOG_FILE
            )
        )
        exit(1)
