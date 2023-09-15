# Author: Myles Scholz
# Created on September 15, 2023
# Description: Module that formats data pulled from iNaturalist.org
import csv


SOURCES_FILE = "config/sources.txt"
HEADER_FORMAT_FILE = "config/header_format.txt"


def get_sources():
    # Read SOURCE_FILE for the sources (iNaturalist projects) to pull data from
    sources = {}
    with open(SOURCES_FILE) as sources_file:
        for line in sources_file:
            line = line.strip(" \r\n")
            line = line.split(",")
            sources[line[0]] = line[1]

    return sources


def read_header_format():
    with open(HEADER_FORMAT_FILE, newline="") as header_file:
        csv_reader = csv.reader(header_file, delimiter="\n")
        output_header = [line[0] for line in csv_reader]

    return output_header


def format_data(sources: dict, observations_dict: dict, output_header: list):
    for source_name in sources:
        for observation in observations_dict[sources[source_name]]:
            print("Formatting observation...")

    print(output_header)


def run(observations_dict: dict):
    # Read the source names and ids (iNaturalist projects)
    sources = get_sources()

    # Read header from config/format_header.csv
    output_header = read_header_format()

    print("Formatting...")
    format_data(sources, observations_dict, output_header)

    print("Done.\n")
