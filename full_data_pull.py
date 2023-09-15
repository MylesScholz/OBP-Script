# Author: Myles Scholz
# Created on September 15, 2023
# Description: Module that pulls data from iNaturalist.org
import csv
import datetime
import json
import traceback

import pyinaturalist
from tqdm import tqdm


SOURCES_FILE = "config/sources.csv"
PLACES_FILE = "places.json"


def get_year():
    # Get the current year
    current_year = datetime.datetime.now().year

    # Get the year to pull data from
    year_input = input("\tYear to Query: ")

    if (
        year_input.isnumeric()
        and len(year_input) == 4
        and int(year_input) <= current_year
    ):
        return year_input
    else:
        print(
            "\tERROR: Invalid year argument, must be a four digit year less than the current year"
        )
        exit(1)


def get_sources():
    # Read SOURCES_FILE for the sources (iNaturalist projects) to pull data from
    with open(SOURCES_FILE, newline="") as sources_file:
        sources = list(csv.DictReader(sources_file))

    return sources


def pull_data(year, sources):
    # If the year is not provided, use the current year
    if year == "" or year is None:
        # In theory, this should be unreachable
        year = str(datetime.datetime.now().year)

    # Set the minimum date of observations to pull to the first day of the year
    min_pull_date = year + "-01-01"

    # Initialize dict to capture results for each source
    observations_dict = {}
    for source in sources:
        print("\tPulling '{}' data...".format(source["Name"]))

        # Pull first page of observation data (maximum of 200 per page)
        reply_dict = pyinaturalist.v1.observations.get_observations(
            d1=min_pull_date, project_id=source["ID"], per_page=200
        )

        page_i = 1
        while page_i * 200 < int(reply_dict["total_results"]):
            page_i += 1
            # Get next 200 entries and append them to results
            reply_dict["results"] += pyinaturalist.v1.observations.get_observations(
                d1=min_pull_date,
                project_id=source["ID"],
                per_page=200,
                page=page_i,
            )["results"]

        observations_dict[source["Abbreviation"]] = reply_dict["results"]

    return observations_dict


def read_places_file():
    with open(PLACES_FILE, "r") as places_file:
        known_places = json.load(places_file)

    return known_places


def write_to_places_file(places):
    with open(PLACES_FILE, "w") as places_file:
        places_file.write(json.dumps(places))


def update_places(sources, observations_dict):
    known_places = read_places_file()

    for source in sources:
        print("\tUpdating places from '{}' data...".format(source["Name"]))

        for observation in tqdm(
            observations_dict[source["Abbreviation"]], desc="\tObservations"
        ):
            place_ids = observation["place_ids"]

            unknown_place_ids = []
            for place_id in place_ids:
                if str(place_id) not in known_places:
                    unknown_place_ids.append(place_id)

            if len(unknown_place_ids) > 0:
                try:
                    reply_dict = pyinaturalist.v1.places.get_places_by_id(
                        unknown_place_ids
                    )
                except Exception:
                    print("\tERROR: Place look-up failed")
                    traceback.print_exc()
                else:
                    for place in reply_dict["results"]:
                        if (
                            place["admin_level"] == 0
                            or place["admin_level"] == 10
                            or place["admin_level"] == 20
                        ):
                            known_places[str(place["id"])] = [
                                str(place["admin_level"]),
                                place["name"],
                            ]

    write_to_places_file(known_places)


def run():
    print("Data Pulling")

    # Get the year to query from the user
    year = get_year()

    # Read the source names and ids to pull from (iNaturalist projects)
    sources = get_sources()

    # Query the iNaturalist API for observations for each project
    observations_dict = pull_data(year, sources)

    # Update known places
    update_places(sources, observations_dict)

    print("Data Pulling => Done\n")

    # TODO: logging

    return observations_dict
