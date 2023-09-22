# Author: Myles Scholz
# Created on September 15, 2023
# Description: Module that pulls data from iNaturalist.org
import csv
import datetime
import json
import os
import traceback

import pyinaturalist
from tqdm import tqdm

# File Name Constants
SOURCES_FILE = "config/sources.csv"
PLACES_FILE = "data/places.json"

# Column Name Constants
SAMPLE_ID_FIELD_NAME = "Sample ID."
BEES_COLLECTED_FIELD_NAME = "Number of bees collected"


def get_year():
    """
    Gets a valid year from the user for querying iNaturalist
    """

    # Get the current year
    current_year = datetime.datetime.now().year

    # Get the year to pull data from
    year_input = input("    Year to Query: ")

    if (
        year_input.isnumeric()
        and len(year_input) == 4
        and int(year_input) <= current_year
    ):
        return year_input
    else:
        print(
            "        ERROR: Invalid year argument, must be a four digit year less than the current year"
        )
        exit(1)


def get_sources():
    # Read SOURCES_FILE for the sources (iNaturalist projects) to pull data from
    with open(SOURCES_FILE, newline="") as sources_file:
        sources = list(csv.DictReader(sources_file))

    return sources


def pull_data(year, sources):
    """
    Pulls observation data for a given year from the sources (iNaturalist projects) listed in config/sources.csv
    """

    # If the year is not provided, use the current year
    if year == "" or year is None:
        # In theory, this should be unreachable
        year = str(datetime.datetime.now().year)

    # Set the minimum date of observations to pull to the first day of the year
    min_pull_date = year + "-01-01"

    # Initialize dict to capture results for each source
    observations_dict = {}
    for source in sources:
        print("    Pulling '{}' data...".format(source["Name"]))

        # Pull first page of observation data (maximum of 200 per page)
        reply_dict = pyinaturalist.v1.observations.get_observations(
            d1=min_pull_date, project_id=source["ID"], per_page=200
        )

        # Calculate the number of pages that need to be pulled
        n_pages = int(reply_dict["total_results"]) // 200
        if int(reply_dict["total_results"]) > n_pages * 200:
            n_pages += 1

        # Pull data in 200 entry increments until all data is captured
        for page_i in tqdm(
            range(2, n_pages + 1),
            desc="        Pages (200 entries)",
            total=n_pages,
            initial=1,
        ):
            # Get next 200 entries and append them to results
            reply_dict["results"] += pyinaturalist.v1.observations.get_observations(
                d1=min_pull_date,
                project_id=source["ID"],
                per_page=200,
                page=page_i,
            )["results"]

        # Store full data for this source under the source's abbreviation in the master dictionary
        observations_dict[source["Abbreviation"]] = reply_dict["results"]

    return observations_dict


def format_str(field):
    # Define empty string as default return value
    field_str = ""

    # Return empty str if field is undefined
    if field is None:
        return field_str

    # Try to convert to str, return field_str regardless
    try:
        field_str = str(field)
    except:
        return field_str

    return field_str


def format_time(time):
    # Check type of time is datetime
    if type(time) != datetime.datetime:
        return ""

    # Translate time to "YYYY-MM-DD HH:MM:SS UTC" format
    time_str = time.strftime("%Y-%m-%d %H:%M:%S UTC")
    return time_str


def format_location(location: list):
    # Check that location list exists
    if location is None:
        return "", ""

    # Return location list with its items converted to strings
    return [format_str(location[0]), format_str(location[1])]


def format_place_ids(place_ids: list):
    # Convert each place_id to str
    str_list = [str(place_id) for place_id in place_ids]
    # Join place_ids with semicolons to avoid CSV errors
    place_ids_str = ";".join(str_list)
    # Wrap the string in brackets and return it
    return "[{}]".format(place_ids_str)


def format_taxon_name(taxon):
    # Check that the taxon field exists
    if taxon is None:
        return ""

    # Check that the taxon name field exists
    if taxon["name"] is None:
        return ""

    # Return the taxon name
    return taxon["name"]


def format_family(identifications):
    # Check that there are identifications to search
    if (
        identifications is None
        or len(identifications) < 1
        or type(identifications) != list
    ):
        return ""

    # Search identifications for taxons with a rank of "family"
    # Return the first one found
    for id in identifications:
        if id["taxon"]["rank"] == "family":
            return id["taxon"]["name"]
        else:
            for ancestor in id["taxon"]["ancestors"]:
                if ancestor["rank"] == "family":
                    return ancestor["name"]

    return ""


def get_ofvs_value(name: str, ofvs: list):
    # Search observations fields (ofvs) for an entry with a matching name
    # and return the associated value
    for field in ofvs:
        if field["name"] == name:
            return format_str(field["value"])

    return ""


def format_observations(observations: list):
    # Initialize an output list
    formatted_observations = []
    # Format each observation
    for observation in observations:
        formatted_observation = {
            "id": format_str(observation["id"]),
            "observed_on_date": observation["observed_on_details"]["date"],
            "observed_on_time": format_time(observation["observed_on"]),
            "user_id": format_str(observation["user"]["id"]),
            "user_login": format_str(observation["user"]["login"]),
            "user_name": format_str(observation["user"]["name"]),
            "created_at": format_time(observation["created_at"]),
            "uri": format_str(observation["uri"]),
            "place_guess": format_str(observation["place_guess"]),
            "latitude": format_location(observation["location"])[0],
            "longitude": format_location(observation["location"])[1],
            "positional_accuracy": format_str(observation["positional_accuracy"]),
            "place_ids": format_place_ids(observation["place_ids"]),
            "taxon_name": format_taxon_name(observation["taxon"]),
            "taxon_family_name": format_family(observation["identifications"]),
            "field_sample_id": get_ofvs_value(
                SAMPLE_ID_FIELD_NAME, observation["ofvs"]
            ),
            "field_bees_collected": get_ofvs_value(
                BEES_COLLECTED_FIELD_NAME, observation["ofvs"]
            ),
        }

        # Add the formatted observation to the output list
        formatted_observations.append(formatted_observation)

    return formatted_observations


def write_observations(observations_dict: dict, sources: list, query_year: str):
    # Get the current date for naming the output folder
    current_date = datetime.datetime.now()
    date_str = "{}_{}_{}".format(
        current_date.month, current_date.day, str(current_date.year)[-2:]
    )

    # Create a separate output file for each source
    for source in sources:
        # Create the output file path for this source
        folder_name = "./data/{}_{}/".format(source["Abbreviation"], date_str)
        file_name = "observations_{}.csv".format(query_year)
        file_path = os.path.relpath(folder_name + file_name)

        print(
            "    Writing '{}' observations to '{}'...".format(source["Name"], file_path)
        )

        # Check for data folder
        if not os.path.isdir("./data"):
            print("ERROR: Data folder must be present")
            exit(1)

        # Create folder if it doesn't exist
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)

        # Get the current source's observations and format them for writing
        source_observations = observations_dict[source["Abbreviation"]]
        formatted_observations = format_observations(source_observations)

        # Write the formatted observations to a CSV
        source_header = formatted_observations[0].keys()
        with open(file_path, "w", newline="") as output_file:
            csv_writer = csv.DictWriter(output_file, fieldnames=source_header)
            csv_writer.writeheader()
            csv_writer.writerows(formatted_observations)


def read_places_file():
    # Check that PLACES_FILE exists; otherwise return an empty dict
    if not os.path.isfile(PLACES_FILE):
        return {}

    # Open places.json and load it as a Python dictionary
    with open(PLACES_FILE, "r") as places_file:
        known_places = json.load(places_file)

    return known_places


def write_to_places_file(places):
    # Write a Python dictionary to places.json
    with open(PLACES_FILE, "w") as places_file:
        places_file.write(json.dumps(places))


def update_places(sources, observations_dict):
    """
    Reads the list of known place IDs from places.json and updates it with new data
    """
    known_places = read_places_file()

    for source in sources:
        print("    Updating places from '{}' data...".format(source["Name"]))

        for observation in tqdm(
            observations_dict[source["Abbreviation"]], desc="        Observations"
        ):
            # Each observation has a list of place IDs (place_ids), which represent
            # various jurisdictions that the observation is under
            place_ids = observation["place_ids"]

            # Create a list of place_ids that are not in places.json
            unknown_place_ids = []
            for place_id in place_ids:
                if str(place_id) not in known_places:
                    unknown_place_ids.append(place_id)

            # Query iNaturalist for the names and administrative level of all unknown_place_ids
            if len(unknown_place_ids) > 0:
                try:
                    reply_dict = pyinaturalist.v1.places.get_places_by_id(
                        unknown_place_ids
                    )
                except Exception:
                    print("        ERROR: Place look-up failed")
                    traceback.print_exc()
                else:
                    # Add the place data to known_places for each place with administrative
                    # level 0, 10, 20 (country, state, and county, respectively)
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

    # Write the new known_places dictionary to places.json
    write_to_places_file(known_places)


def run():
    print("Data Pulling")

    # Get the year to query from the user
    year = get_year()

    # Read the source names and ids to pull from (iNaturalist projects)
    sources = get_sources()

    print()

    # Query the iNaturalist API for observations for each project
    observations_dict = pull_data(year, sources)

    print()

    # Write the observations (with some reformatting) to a CSV in the data folder
    write_observations(observations_dict, sources, year)

    print()

    # Update known places
    update_places(sources, observations_dict)

    print("Data Pulling => Done\n")

    # TODO: logging

    return observations_dict
