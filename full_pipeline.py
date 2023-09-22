# Author: Myles Scholz
# Created on September 15, 2023
# Description: Executes the full data pipeline for updating the Oregon Bee Atlas database
import pickle

import full_data_pull as fdp
import full_format_data as ffd
import full_merge_data as fmd
import full_create_labels as fcl


def main():
    # observations_dict = fdp.run()
    # with open("observations_dict.pkl", "wb") as file:
    #     pickle.dump(observations_dict, file, pickle.HIGHEST_PROTOCOL)

    with open("observations_dict.pkl", "rb") as file:
        observations_dict = pickle.load(file)
    formatted_dict = ffd.run(observations_dict)
    with open("formatted_dict.pkl", "wb") as file:
        pickle.dump(formatted_dict, file, pickle.HIGHEST_PROTOCOL)

    # with open("formatted_dict.pkl", "rb") as file:
    #     formatted_dict = pickle.load(file)
    # merged_dataset = fmd.run(formatted_dict)
    # with open("merged_dataset.pkl", "wb") as file:
    #     pickle.dump(merged_dataset, file, pickle.HIGHEST_PROTOCOL)

    # with open("merged_dataset.pkl", "rb") as file:
    #     merged_dataset = pickle.load(file)
    # fcl.run(merged_dataset)


if __name__ == "__main__":
    main()
