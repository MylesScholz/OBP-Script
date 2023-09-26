# Author: Myles Scholz
# Created on September 15, 2023
# Description: Executes the full data pipeline for updating the Oregon Bee Atlas database
import csv
import pickle

import full_data_pull as fdp
import full_format_data as ffd
import full_merge_data as fmd
import full_create_labels as fcl


def read_dataset(file_path: str):
    try:
        with open(file_path, "r", newline="") as dataset_file:
            dataset = list(csv.DictReader(dataset_file))

        return dataset
    except:
        print("ERROR: could not open '{}'".format(file_path))


def confirm_label_input(merged_output_file: str):
    print(
        "WARNING: Creating labels takes a long time. Please check that the ",
        " data in '{}' is properly formatted to avoid costly errors.".format(
            merged_output_file
        ),
        " Make sure to save any changes before continuing.\n",
        sep="",
    )
    response = input(
        "Enter 'Y' to continue with label creation or 'N' to stop the program"
        " without creating labels: "
    )
    if response.lower() == "y":
        print("\n")
        return read_dataset(merged_output_file)

    exit(0)


def main():
    # observations_dict = fdp.run()

    # with open("observations_dict.pkl", "wb") as file:
    #     pickle.dump(observations_dict, file, pickle.HIGHEST_PROTOCOL)

    # with open("observations_dict.pkl", "rb") as file:
    #     observations_dict = pickle.load(file)

    # formatted_dict = ffd.run(observations_dict)

    # with open("formatted_dict.pkl", "wb") as file:
    #     pickle.dump(formatted_dict, file, pickle.HIGHEST_PROTOCOL)

    # with open("formatted_dict.pkl", "rb") as file:
    #     formatted_dict = pickle.load(file)

    # merged_output_file = fmd.run(formatted_dict)

    # with open("merged_output_file.pkl", "wb") as file:
    #     pickle.dump(merged_output_file, file, pickle.HIGHEST_PROTOCOL)

    # with open("merged_output_file.pkl", "rb") as file:
    #     merged_output_file = pickle.load(file)

    merged_output_file = "../ALL_merged.csv"
    merged_dataset = confirm_label_input(merged_output_file)

    fcl.run(merged_dataset)


if __name__ == "__main__":
    main()
