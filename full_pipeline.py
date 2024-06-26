# Author: Myles Scholz
# Created on September 15, 2023
# Description: Executes the full data pipeline for updating the Oregon Bee Atlas database
import csv
import os
import sys
import tkinter as tk
from tkinter import filedialog

import full_data_pull as fdp
import full_format_data as ffd
import full_merge_data as fmd
import full_create_labels as fcl


def get_dataset_file_path():
    """
    Gets a file path from the user that points to an existing CSV file.
    Used when a file path is not provided programmatically ("labels only" mode).
    """
    dataset_file_path = ""

    root = tk.Tk()
    root.attributes("-alpha", 0.0)
    root.attributes("-topmost", True)

    # Get user input until they provide a valid file path or quit
    print("Dataset File: the file to create labels from\n")
    while dataset_file_path == "":
        # Prompt the user
        file_path_response = filedialog.askopenfilename(
            initialdir="../", filetypes=[("CSV Files", "*.csv")], parent=root
        )

        print(file_path_response)

        # Check the response for one of the options
        if file_path_response.lower() == "":
            exit(0)
        elif not os.path.isfile(file_path_response):
            print("ERROR: file does not exist\n")
        elif not file_path_response.lower().endswith(".csv"):
            print("ERROR: file is not a CSV file\n")
        else:
            # Reduce the file path to a relative path and set it to be returned
            dataset_file_path = os.path.relpath(file_path_response)

    root.destroy()
    return dataset_file_path


def read_dataset(file_path: str):
    # Try opening the file and reading it as a list
    try:
        with open(file_path, "r", newline="") as dataset_file:
            dataset = list(csv.DictReader(dataset_file))

        return dataset
    except:
        # Print an error and end the program if unsuccessful
        print("ERROR: could not open '{}'".format(file_path))
        exit(1)


def confirm_label_input(merged_output_file: str):
    # Notify the user of the time cost of the labels process
    print(
        "WARNING: Creating labels takes a long time. Please check that the ",
        " data in '{}' is properly formatted to avoid costly errors.".format(
            merged_output_file
        ),
        " Make sure to save any changes before continuing.\n",
        sep="",
    )
    # Get confirmation to continue from the user
    response = input(
        "Enter 'Y' to continue with label creation or any other key to quit: "
    )
    if response.lower() == "y":
        print()
        # Read data from the given file and return it
        return read_dataset(merged_output_file)

    # End the program if the user enter anything but 'Y' or 'y'
    exit(0)


def main():
    # Pull, format, and merge data if not in "labels only" mode
    if "--labels-only" not in sys.argv:
        # Pull data
        observations_dict = fdp.run()

        # Format data
        formatted_dict = ffd.run(observations_dict)

        # Merge data with a pre-exisiting dataset
        dataset_file_path = fmd.run(formatted_dict)

        # Confirm the input to the labels process with the user to avoid costly errors
        dataset = confirm_label_input(dataset_file_path)
    else:
        # In "labels only" mode, get a file path from the user to make labels from
        dataset_file_path = get_dataset_file_path()

        # Read the dataset into memory
        dataset = read_dataset(dataset_file_path)

    # Create labels
    fcl.run(dataset)


if __name__ == "__main__":
    main()
