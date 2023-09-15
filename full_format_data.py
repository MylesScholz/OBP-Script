# Author: Myles Scholz
# Created on September 15, 2023
# Description: Module that formats data pulled from iNaturalist.org
import csv


SOURCES_FILE = "config/sources.csv"
HEADER_FORMAT_FILE = "config/header_format.txt"


def get_sources():
    # Read SOURCES_FILE for the sources (iNaturalist projects) to pull data from
    with open(SOURCES_FILE, newline="") as sources_file:
        sources = list(csv.DictReader(sources_file))

    return sources


def read_header_format():
    with open(HEADER_FORMAT_FILE, newline="") as header_file:
        csv_reader = csv.reader(header_file, delimiter="\n")
        output_header = [line[0] for line in csv_reader]

    return output_header


def format_data(sources: list, observations_dict: dict, output_header: list):
    # Initialize formatted output dictionary
    formatted_dict = {}

    for source in sources:
        print("    Formatting '{}' data...".format(source["Name"]))

        # Divide the formatted output dictionary by source
        formatted_dict[source["Abbreviation"]] = []

        for observation in observations_dict[source["Abbreviation"]]:
            formatted_observation = {}

            # Add the six blank fields at the start of the formatted output
            # (Verified, Date Added, Date Label Print, Date Label Sent, Observation No., and Voucher No.)
            for i in range(6):
                formatted_observation[output_header[i]] = ""

            # iNaturalist ID
            formatted_observation[output_header[6]] = observation["user"]["id"]

            # iNaturalist Alias
            formatted_observation[output_header[7]] = observation["user"]["login"]

            # TODO: format the remaining columns

            # Collector - First Name
            # Collector - First Initial
            # Collector - Last Name
            formatted_observation[output_header[8]] = ""
            formatted_observation[output_header[9]] = ""
            formatted_observation[output_header[10]] = ""

            # Sample ID
            formatted_observation[output_header[11]] = ""

            # Specimen ID
            formatted_observation[output_header[12]] = ""

            # Collection Day 1
            # Month 1
            # Year 1
            # Time 1
            formatted_observation[output_header[13]] = ""
            formatted_observation[output_header[14]] = ""
            formatted_observation[output_header[15]] = ""
            formatted_observation[output_header[16]] = ""

            # Collection Day 2
            # Month 2
            # Year 2
            # Time 2
            formatted_observation[output_header[17]] = ""
            formatted_observation[output_header[18]] = ""
            formatted_observation[output_header[19]] = ""
            formatted_observation[output_header[20]] = ""

            # Collect Date 2 Merge
            formatted_observation[output_header[21]] = ""

            # Country
            formatted_observation[output_header[22]] = ""

            # State
            formatted_observation[output_header[23]] = ""

            # County
            formatted_observation[output_header[24]] = ""

            # Location
            formatted_observation[output_header[25]] = ""

            # Collection Site Description
            formatted_observation[output_header[26]] = ""

            # Abbreviated Location
            formatted_observation[output_header[27]] = ""

            # Dec. Lat.
            # Dec. Long.
            formatted_observation[output_header[28]] = ""
            formatted_observation[output_header[29]] = ""

            # Lat/Long Accuracy
            formatted_observation[output_header[30]] = ""

            # Elevation
            formatted_observation[output_header[31]] = ""

            # Collection method
            formatted_observation[output_header[32]] = ""

            # Associated plant - family
            # Associated plant - genus, species
            # Associated plant - Inaturalist URL
            formatted_observation[output_header[33]] = ""
            formatted_observation[output_header[34]] = ""
            formatted_observation[output_header[35]] = ""

            # Add the eight blank fields at the end of the formatted output
            # (Det. Volunteer - Family, Det. Volunteer - Genus, Det. Volunteer - Species,
            #  Det. Volunteer - Sex/Caste, Det LR Best - Genus, Det. LR Best - Species,
            #  Det LR Best - Sex/Caste)
            for i in range(7):
                formatted_observation[output_header[36 + i]] = ""

            # TODO: Append the formatted observation, expanding by the number of bees collected

            # formatted_dict[source["Abbreviation"]].append(formatted_observation)


def run(observations_dict: dict):
    print("Data Formatting")

    # Read the source names and ids (iNaturalist projects)
    sources = get_sources()

    # Read header from config/format_header.csv
    output_header = read_header_format()

    # Create a re-formatted dictionary containing the data
    formatted_dict = format_data(sources, observations_dict, output_header)

    print("Data Formatting => Done\n")

    # TODO: logging

    return formatted_dict
