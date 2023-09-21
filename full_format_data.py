# Author: Myles Scholz
# Created on September 15, 2023
# Description: Module that formats data pulled from iNaturalist.org
import csv
import datetime
import json
import os

from tqdm import tqdm


# File Name Constants
SOURCES_FILE = "config/sources.csv"
HEADER_FORMAT_FILE = "config/header_format.txt"
USER_NAMES_FILE = "data/usernames.csv"
PLACES_FILE = "places.json"

# Folder Name Constant
ELEVATION_DATA_FOLDER = "data/elevation/"

# Column Name Constants
SAMPLE_ID_FIELD_NAME = "Sample ID."
BEES_COLLECTED_FIELD_NAME = "Number of bees collected"


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


def format_str(field: str):
    if field is None:
        return ""

    return str(field)


def format_name(user_login: str, user_name: str):
    user_first_name = user_first_initial = user_last_name = ""

    # Check usernames.csv for manually entered name
    with open(USER_NAMES_FILE, "r") as user_names_file:
        for row in user_names_file:
            # Remove trailing characters and split line into array
            row = row.rstrip("\r\n")
            row = row.split(",")

            if row[1] == user_login:
                user_full_name_split = row[0].split(" ")
                # User first name has caveats as below
                user_first_name = user_full_name_split[0]
                user_first_initial = user_first_name[0] + "."

                # User last name has caveats as below
                user_last_name = user_full_name_split[-1]

    # If name still unassigned, check user_full_name (from iNaturalist)
    if (
        user_first_name == ""
        and user_first_initial == ""
        and user_last_name == ""
        and user_name != ""
        and user_name is not None
    ):
        user_full_name_split = user_name.split(" ")

        # User first name assumed to be the first space-separated word in their full name
        # This will not capture middle names or compound first names (e.g., Mary Jo)
        if user_first_name == "":
            user_first_name = user_full_name_split[0]
            user_first_initial = user_first_name[0] + "."

        # User last name assumed to be the last space-separated word in their full name
        # This will not capture middle names or compound last names (e.g., van Horn)
        # If there is only one name provided, the last name will be empty
        if len(user_full_name_split) > 1 and user_last_name == "":
            user_last_name = user_full_name_split[-1]

    return user_first_name, user_first_initial, user_last_name


def get_ofvs_value(name: str, ofvs: list):
    # Search observations fields (ofvs) for an entry with a matching name
    # and return the associated value
    for field in ofvs:
        if field["name"] == name:
            return format_str(field["value"])

    return ""


def format_month(decimal_month: str):
    if decimal_month is None:
        return ""

    month_numerals = [
        "I",
        "II",
        "III",
        "IV",
        "V",
        "VI",
        "VII",
        "VIII",
        "IX",
        "X",
        "XI",
        "XIII",
    ]

    return month_numerals[int(decimal_month) - 1]


def format_time(observed_on):
    if observed_on is None or type(observed_on) != datetime.datetime:
        return ""

    time = str(observed_on.hour) + observed_on.strftime(":%M")

    return time


def read_places_file():
    with open(PLACES_FILE, "r") as places_file:
        known_places = json.load(places_file)

    return known_places


def look_up_place(place_ids: list):
    country = state = county = ""

    # Look up place IDs in places.jscon
    known_places = read_places_file()
    for place_id in place_ids:
        if str(place_id) in known_places:
            place = known_places[str(place_id)]

            if place[0] == "0":
                country = place[1]
            if place[0] == "10":
                state = place[1]
            if place[0] == "20":
                county = place[1]

    return country, state, county


def format_state(state_name: str):
    if state_name is None:
        return ""

    # Abbreviate state if possible
    abbreviation = state_name

    # Dictionary of USPS abbreviations for US states
    state_abbreviations = {
        "Alabama": "AL",
        "Alaska": "AK",
        "Arizona": "AZ",
        "Arkansas": "AR",
        "California": "CA",
        "Colorado": "CO",
        "Connecticut": "CT",
        "Delaware": "DE",
        "Florida": "FL",
        "Georgia": "GA",
        "Hawaii": "HI",
        "Idaho": "ID",
        "Illinois": "IL",
        "Indiana": "IN",
        "Iowa": "IA",
        "Kansas": "KS",
        "Kentucky": "KY",
        "Louisiana": "LA",
        "Maine": "ME",
        "Maryland": "MD",
        "Massachusetts": "MA",
        "Michigan": "MI",
        "Minnesota": "MN",
        "Mississippi": "MS",
        "Missouri": "MO",
        "Montana": "MT",
        "Nebraska": "NE",
        "Nevada": "NV",
        "New Hampshire": "NH",
        "New Jersey": "NJ",
        "New Mexico": "NM",
        "New York": "NY",
        "North Carolina": "NC",
        "North Dakota": "ND",
        "Ohio": "OH",
        "Oklahoma": "OK",
        "Oregon": "OR",
        "Pennsylvania": "PA",
        "Rhode Island": "RI",
        "South Carolina": "SC",
        "South Dakota": "SD",
        "Tennessee": "TN",
        "Texas": "TX",
        "Utah": "UT",
        "Vermont": "VT",
        "Virginia": "VA",
        "Washington": "WA",
        "West Virginia": "WV",
        "Wisconsin": "WI",
    }

    if state_name in state_abbreviations:
        abbreviation = state_abbreviations[state_name]

    return abbreviation


def format_location(place_guess):
    """
    Parses a comma-separated place guess for a specific location name.
    Assumes the location name is the first item.
    """
    if place_guess is None or place_guess == "":
        return ""

    place_guess_split = place_guess.split(", ")

    if len(place_guess_split) > 1:
        return place_guess_split[0]

    return ""


def format_coordinates(location):
    if location is None:
        return "", ""

    latitude = longitude = ""

    if location[0] is not None:
        latitude = "{:.4f}".format(float(location[0]))

    if location[1] is not None:
        longitude = "{:.4f}".format(float(location[1]))

    return latitude, longitude


def read_hgt(file_path: str, latitude: str, longitude: str):
    with open(file_path, "rb") as file:
        latitude_decimal_part = float(latitude) - int(float(latitude))
        # Convert from decimal to arcseconds (each column is an arcsecond)
        row = int(latitude_decimal_part * 3600) % 3600
        # Take the complement of the row because files are read from top to bottom
        row = 3601 - row

        longitude_decimal_part = float(longitude) - int(float(longitude))
        # Convert from decimal to arcseconds (each row is an arcsecond)
        column = int(longitude_decimal_part * 3600) % 3600

        # Skip to the desired row in the input stream
        # There are 3601 columns per row because the edges of the data files overlap
        # Each data point is 2-bytes and the data is in row-major order
        # Subtract 1 from the row so it doesn't skip the desired row
        file.seek((2 * 3601 * (row - 1)) + (2 * column))

        # Read data point and convert it to an integer
        # The data is stored in big-endian byte ordering and is signed
        data_point = file.read(2)
        data_int = int.from_bytes(data_point, byteorder="big", signed=True)
        return str(data_int)


def format_elevation(latitude: str, longitude: str):
    """
    Looks up elevation for a given longitude and latitude using data from
    the Shuttle Radar Topography Mission (SRTMGL1), which is stored in
    /data/elevation_data/

    The data has 1 arcsecond (~30m) resolution

    :param latitude: latitude to look up
    :param longitude: longitude to look up
    """

    # Check that latitude and longitude are provided
    if latitude == "" or longitude == "":
        return ""

    # Take integer part of given latitude and longitude
    cardinal_latitude = latitude.split(".")[0]
    cardinal_longitude = longitude.split(".")[0]

    # Replace sign with cardinal direction
    if int(cardinal_latitude) < 0:
        # The data files are named by the southwestern corner of the area they cover.
        # If the provided latitude is negative (south), we must use the data file for the
        # next data file to the south, assuming there is a decimal part to the latitude
        cardinal_latitude = "S" + str(int(cardinal_latitude[1:]) + 1)
    else:
        cardinal_latitude = "N" + cardinal_latitude

    if int(cardinal_longitude) < 0:
        # The data files are named by the southwestern corner of the area they cover
        # If the provided longitude is negative (west), we must use the data file for the
        # next data file to the west, assuming there is a decimal part to the longitude
        cardinal_longitude = "W" + str(int(cardinal_longitude[1:]) + 1)
    else:
        cardinal_longitude = "E" + cardinal_longitude

    # Construct the relevant data file path
    # .hgt is a binary data file format used by SRTM
    elevation_data_file_path = (
        ELEVATION_DATA_FOLDER + cardinal_latitude + cardinal_longitude + ".hgt"
    )

    if not os.path.isfile(elevation_data_file_path):
        return ""

    elevation = read_hgt(elevation_data_file_path, latitude, longitude)

    return elevation


def format_family(identifications):
    if (
        identifications is None
        or len(identifications) < 1
        or type(identifications) != list
    ):
        return ""

    for id in identifications:
        if id["taxon"]["rank"] == "family":
            return id["taxon"]["name"]
        else:
            for ancestor in id["taxon"]["ancestors"]:
                if ancestor["rank"] == "family":
                    return ancestor["name"]

    return ""


def format_scientific_name(taxon):
    if taxon is None:
        return ""

    if taxon["name"] is None:
        return ""

    return taxon["name"]


def format_data(sources: list, observations_dict: dict, output_header: list):
    # Initialize formatted output dictionary
    formatted_dict = {}

    for source in sources:
        print("    Formatting '{}' data...".format(source["Name"]))

        # Divide the formatted output dictionary by source
        formatted_dict[source["Abbreviation"]] = []

        for observation in tqdm(
            observations_dict[source["Abbreviation"]], desc="        Observations"
        ):
            formatted_observation = {}

            # Add the six blank fields at the start of the formatted output
            # (Verified, Date Added, Date Label Print, Date Label Sent, Observation No., and Voucher No.)
            for i in range(6):
                formatted_observation[output_header[i]] = ""

            # iNaturalist ID
            formatted_observation[output_header[6]] = format_str(
                observation["user"]["id"]
            )

            # iNaturalist Alias
            formatted_observation[output_header[7]] = format_str(
                observation["user"]["login"]
            )

            # Collector - First Name
            # Collector - First Initial
            # Collector - Last Name
            user_first_name, user_first_initial, user_last_name = format_name(
                observation["user"]["login"], observation["user"]["name"]
            )

            formatted_observation[output_header[8]] = user_first_name
            formatted_observation[output_header[9]] = user_first_initial
            formatted_observation[output_header[10]] = user_last_name

            # Sample ID
            formatted_observation[output_header[11]] = get_ofvs_value(
                SAMPLE_ID_FIELD_NAME, observation["ofvs"]
            )

            # Specimen ID
            formatted_observation[output_header[12]] = get_ofvs_value(
                BEES_COLLECTED_FIELD_NAME, observation["ofvs"]
            )

            # Collection Day 1
            # Month 1
            # Year 1
            # Time 1
            observed_on_details = observation["observed_on_details"]

            formatted_observation[output_header[13]] = format_str(
                observed_on_details["day"]
            )
            formatted_observation[output_header[14]] = format_month(
                observed_on_details["month"]
            )
            formatted_observation[output_header[15]] = format_str(
                observed_on_details["year"]
            )
            formatted_observation[output_header[16]] = format_time(
                observation["observed_on"]
            )

            # Collection Day 2 (blank)
            # Month 2 (blank)
            # Year 2 (blank)
            # Time 2 (blank)
            # Collect Date 2 Merge (blank)
            formatted_observation[output_header[17]] = ""
            formatted_observation[output_header[18]] = ""
            formatted_observation[output_header[19]] = ""
            formatted_observation[output_header[20]] = ""
            formatted_observation[output_header[21]] = ""

            # Country
            # State
            # County
            country, state, county = look_up_place(observation["place_ids"])

            formatted_observation[output_header[22]] = country
            formatted_observation[output_header[23]] = format_state(state)
            formatted_observation[output_header[24]] = county

            # Location
            location = format_location(observation["place_guess"])
            formatted_observation[output_header[25]] = location

            # Collection Site Description (blank)
            formatted_observation[output_header[26]] = ""

            # Abbreviated Location
            formatted_observation[output_header[27]] = location

            # Dec. Lat.
            # Dec. Long.
            latitude, longitude = format_coordinates(observation["location"])

            formatted_observation[output_header[28]] = latitude
            formatted_observation[output_header[29]] = longitude

            # Lat/Long Accuracy
            formatted_observation[output_header[30]] = format_str(
                observation["positional_accuracy"]
            )

            # Elevation
            formatted_observation[output_header[31]] = format_elevation(
                latitude, longitude
            )

            # Collection method (blank)
            formatted_observation[output_header[32]] = ""

            # Associated plant - family
            # Associated plant - genus, species
            # Associated plant - Inaturalist URL
            formatted_observation[output_header[33]] = format_family(
                observation["identifications"]
            )
            formatted_observation[output_header[34]] = format_scientific_name(
                observation["taxon"]
            )
            formatted_observation[output_header[35]] = format_str(observation["uri"])

            # Add the eight blank fields at the end of the formatted output
            # (Det. Volunteer - Family, Det. Volunteer - Genus, Det. Volunteer - Species,
            #  Det. Volunteer - Sex/Caste, Det LR Best - Genus, Det. LR Best - Species,
            #  Det LR Best - Sex/Caste)
            for i in range(7):
                formatted_observation[output_header[36 + i]] = ""

            specimen_id = formatted_observation[output_header[12]]
            if specimen_id != "":
                try:
                    specimen_id = int(specimen_id)
                except ValueError:
                    formatted_dict[source["Abbreviation"]].append(formatted_observation)
                else:
                    if specimen_id >= 1:
                        for i in range(1, specimen_id + 1):
                            dup_observation = formatted_observation.copy()
                            dup_observation[output_header[12]] = str(i)

                            formatted_dict[source["Abbreviation"]].append(
                                dup_observation
                            )

    return formatted_dict


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
