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
        # Divide the formatted output dictionary by source
        formatted_dict[source["Abbreviation"]] = []

        for observation in observations_dict[source["Abbreviation"]]:
            print("\tFormatting observation...")

    print("\t", output_header)


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
