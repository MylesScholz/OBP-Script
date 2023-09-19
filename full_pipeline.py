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

    # print("Merging data with database...")
    # fmd.run()

    # print("Creating labels...")
    # fcl.run()


if __name__ == "__main__":
    main()
