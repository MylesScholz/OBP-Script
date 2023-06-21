from dataclasses import replace
from sqlite3 import Timestamp
from urllib.error import HTTPError
import pyinaturalist
import datetime
import json
import csv
import os
import sys
import time
import requests

# Project names to pull data from
PROJECTNAME = "oregon-bee-atlas-plant-images-sampleid"
PROJECTNAMEOUTSIDE = "master-melittologist-outside-of-oregon"
# Attributes to be included in the .csv file
OBSERVATIONATTRIBUES = [
    "id",
    "observed_on",
    "time_observed_at",
    "user_id",
    "user_login",
    "created_at",
    "url",
    "place_guess",
    "latitude",
    "longitude",
    "positional_accuracy",
    "place_county_name",
    "place_state_name",
    "place_country_name",
    "scientific_name",
    "taxon_family_name",
    "field:sample id.",
    "field:number of bees collected",
]
# Name of observation fields Sample ID key
SAMPLEIDNAME = "Sample ID."
# Name of observation fields Bees collected key
BEESCOLLECTEDNAME = "Number of bees collected"
# API documentation for places is incorrect, admin levels are as follows:
# County - 20
# State- 10
# Country - 0
COUNTYADMINLEVEL = 20
STATEADMINLEVEL = 10
COUNTRYADMINLEVEL = 0
# File to track known places name
KNOWNPLACESFILENAME = "places.json"


# Class to contain observaion fields of interest
class Observation:
    id = None
    observed_on = None
    time_observed_at = None
    user_id = None
    user_login = None
    created_at = None
    url = None
    place_guess = None
    latitude = None
    longitude = None
    positional_accuracy = None
    place_county_name = None
    place_state_name = None
    place_country_name = None
    scientific_name = None
    taxon_family_name = None
    field_sample_id = None
    field_number_of_bees_collected = None

    def __init__(self, d):
        self.id = d["id"]
        self.observed_on = d["observed_on_details"]["date"]
        self.time_observed_at = translate_time(d["observed_on"])
        self.user_id = d["user"]["id"]
        self.user_login = d["user"]["login"]
        self.created_at = translate_time(d["created_at"])
        self.url = d["uri"]
        self.place_guess = d["place_guess"]
        self.latitude = d["location"][0]
        self.longitude = d["location"][1]
        self.positional_accuracy = d["positional_accuracy"]

        self.scientific_name = d["taxon"]["name"]

        # Search through observation identifications for family taxon
        if d["identifications"] is not None and len(d["identifications"]) > 0:
            for id in d["identifications"]:
                # Check if observation is a family
                if id["taxon"]["rank"] == "family":
                    self.taxon_family_name = id["taxon"]["name"]
                else:
                    # Check ancestors for a family
                    self.taxon_family_name = get_family_name(id["taxon"]["ancestors"])
                if self.taxon_family_name != "":
                    break
        else:
            self.taxon_family_name = ""

        # Field observations
        self.field_sample_id = get_value_from_ofvs(SAMPLEIDNAME, d["ofvs"])
        self.field_number_of_bees_collected = get_value_from_ofvs(
            BEESCOLLECTEDNAME, d["ofvs"]
        )


def translate_time(time):
    """ "
    Translate time value from observations into UTC YYYY-MM-DD HH:MM:SS format
    """

    # Ensure time is a datetime value (not garunteed)
    if type(time) != type(datetime.datetime.now()):
        return ""

    # Translate time to UTC
    timeStamp = datetime.datetime.timestamp(time)
    utcTime = datetime.datetime.fromtimestamp(timeStamp, tz=datetime.timezone.utc)

    # Translate time to YYYY-MM-DD HH:MM:SS format
    stringTime = str(utcTime)
    stringTime = stringTime[:19] + " UTC"
    return stringTime


def get_places(placeIds, knownPlaces):
    """
    Check placeIds against known places from reference file, and if not found,
    pull places from iNaturalist API based on provided ids. Update known places with any new values,
    and return a tuple of (updated knownPlaces, array of Country, State, and County)
    """

    placeArray = ["", "", ""]

    # Check place ids against known places
    for p in placeIds:
        if str(p) in knownPlaces:
            placeData = knownPlaces[str(p)]
            if placeData[0] == "0":
                placeArray[0] = placeData[1]
            elif placeData[0] == "10":
                placeArray[1] = placeData[1]
            elif placeData[0] == "20":
                placeArray[2] = placeData[1]

    # If we have all places, no need to call API
    if placeArray[0] != "" and placeArray[1] != "" and placeArray[2] != "":
        return (placeArray, knownPlaces)

    # API has a limit of 100/minute. Since we don't care how long this script takes to run (within limits), wait so we don't hit that limit
    time.sleep(1)
    # Get places based on id and update known places with found values
    try:
        places = pyinaturalist.v1.places.get_places_by_id(placeIds)
    except requests.exceptions.HTTPError:
        return (placeArray, knownPlaces)
    else:
        for p in places["results"]:
            if p["admin_level"] == 0:
                if placeArray[0] == "":
                    placeArray[0] = p["name"]
                    knownPlaces[str(p["id"])] = ["0", p["name"]]
            elif p["admin_level"] == 10:
                if placeArray[1] == "":
                    placeArray[1] = p["name"]
                    knownPlaces[str(p["id"])] = ["10", p["name"]]
            elif p["admin_level"] == 20:
                if placeArray[2] == "":
                    placeArray[2] = p["name"]
                    knownPlaces[str(p["id"])] = ["20", p["name"]]

        return (placeArray, knownPlaces)


def write_to_place_file(knownPlaces):
    """
    Write knownPlaces dictionary to places.json file
    """
    file = open("./" + KNOWNPLACESFILENAME, "w")
    file.write(json.dumps(knownPlaces))
    file.close()


def read_place_file():
    """
    Read knownPlaces dictionary from places.json file
    """
    file = open("./" + KNOWNPLACESFILENAME, "r")
    places = json.load(file)
    file.close()
    return places


def get_family_name(ancestors):
    """
    Search ancestors for one ranked as a family and return its name
    """
    for anc in ancestors:
        if anc["rank"] == "family":
            return anc["name"]
    return ""


def get_value_from_ofvs(name, ofvs):
    """
    Search observation fields for one matching the name, and return its value
    """
    for o in ofvs:
        if o["name"] == name:
            return o["value"]
    return ""


def get_observations(outside, year):
    """
    Get all observations, project pulled from depends on outside value for values outside Oregon, and year minimum can be specified
    """

    # Set to outside Oregon project if requested
    projectId = PROJECTNAME
    if outside:
        projectId = PROJECTNAMEOUTSIDE

    currentDate = datetime.datetime.now()
    currentYear = str(currentDate.year)
    minPullDate = currentYear + "-01-01 00:00:00.000000"

    # Set year if requested
    if year != "":
        minPullDate = year + "-01-01 00:00:00.000000"

    # Get observations from first of the year to current date
    observationsDict = pyinaturalist.v1.observations.get_observations(
        d1=minPullDate, project_id=projectId, per_page=200
    )

    # Only 200 are returned at a time, if the total is more, we need to call the API again
    if int(observationsDict["total_results"]) > 200:
        i = 1
        while i * 200 < int(observationsDict["total_results"]):
            i = i + 1
            # API has a limit of 100/minute. Since we don't care how long this script takes to run, wait so we don't hit that limit
            time.sleep(1)
            # Get next 200 entries and append them to results
            observationsDict["results"] = (
                observationsDict["results"]
                + pyinaturalist.v1.observations.get_observations(
                    d1=minPullDate, project_id=projectId, per_page=200, page=i
                )["results"]
            )
    return observationsDict


def none_to_empty_string(observation):
    """
    Ensure no None values exist in observaion data when a value is expected
    """
    if observation["id"] is None:
        observation["id"] = ""
    if observation["observed_on_details"]["date"] is None:
        observation["observed_on_details"]["date"] = ""
    if observation["observed_on"] is None:
        observation["observed_on"] = ""
    if observation["user"]["id"] is None:
        observation["user"]["id"] = ""
    if observation["user"]["login"] is None:
        observation["user"]["login"] = ""
    if observation["created_at"] is None:
        observation["created_at"] = ""
    if observation["uri"] is None:
        observation["uri"] = ""
    if observation["place_guess"] is None:
        observation["place_guess"] = ""
    if observation["location"] is None:
        observation["location"] = ["", ""]
    if observation["positional_accuracy"] is None:
        observation["positional_accuracy"] = ""
    if observation["taxon"] is None:
        observation["taxon"] = {}
        observation["taxon"]["name"] = ""
    if observation["taxon"]["name"] is None:
        observation["taxon"]["name"] = ""
    return observation


def write_observations(dict, fileName):
    """
    Write all observations to .csv file
    """
    knownPlaces = read_place_file()
    i = len(dict["results"])
    # Iterate over each observation
    while i > 0:
        i = i - 1
        obv = dict["results"][i]

        # Ensure data is present where expected
        obv = none_to_empty_string(obv)

        # Convert to Observation object
        o = Observation(obv)

        # Find Country, State, and County
        places, knownPlaces = get_places(obv["place_ids"], knownPlaces)
        o.place_country_name = places[0]
        o.place_state_name = places[1]
        o.place_county_name = places[2]

        # Write the Observation to .csv file
        write_to_csv(o, fileName)

    # Update knownPlaces with any new entries
    write_to_place_file(knownPlaces)


def prepare_data_file(outside):
    """
    Ensure folders are in place, and create a .csv file with header values to write to
    """

    # Create folder name
    currentDate = str(datetime.datetime.now())[:10]
    folderName = currentDate.replace("-", "_")
    folderName = folderName[5:] + "_" + folderName[2:4]
    if outside:
        folderName = "o_" + folderName

    # Check for data folder
    if not os.path.isdir("./data"):
        print("ERROR: Data folder must be present")
        exit(2)

    # Create folder
    if not os.path.isdir("./data/" + folderName):
        os.makedirs("./data/" + folderName)

    # Create .csv file
    fileName = "./data/" + folderName + "/observations.csv"
    write_header_to_csv(fileName)
    return fileName


def write_to_csv(observation, fileName):
    """
    Write an observation to a .csv file
    """
    file = open(fileName, "a")
    writer = csv.writer(file, delimiter=",", lineterminator="\n")
    writer.writerow(
        [
            observation.id,
            observation.observed_on,
            observation.time_observed_at,
            observation.user_id,
            observation.user_login,
            observation.created_at,
            observation.url,
            observation.place_guess,
            observation.latitude,
            observation.longitude,
            observation.positional_accuracy,
            observation.place_county_name,
            observation.place_state_name,
            observation.place_country_name,
            observation.scientific_name,
            observation.taxon_family_name,
            observation.field_sample_id,
            observation.field_number_of_bees_collected,
        ]
    )
    file.close()


def parse_cmd_line():
    """
    Parse command line arguments, checking for values on --outside and --year
    """

    outside = "0"
    year = ""
    yearArg = False
    i = 0

    # Retrieve arguments
    for arg in sys.argv:
        if arg == "--outside":
            if i + 1 >= len(sys.argv):
                print("ERROR: --outside argument not set")
                exit(1)
            outside = sys.argv[i + 1]
        elif arg == "--year":
            # No year value is treated as current year wanted
            if not (i + 1 >= len(sys.argv)):
                yearArg = True
                year = sys.argv[i + 1]
        i += 1

    # Ensure year is in correct format
    if yearArg:
        currentYear = datetime.datetime.now().year
        if year.isnumeric() and int(year) >= currentYear:
            print("ERROR: Year argument must be less than current year")
            exit(1)
        elif not year.isnumeric() or len(year) != 4:
            print(
                "ERROR: Invalid year argument, must be a four digit year less than the current year"
            )
            exit(1)

    # Ensure outside is in correct format
    if not outside.isnumeric() or (int(outside) != 0 and int(outside) != 1):
        print("ERROR: Invalid outside argument, must be 0 or 1")
        exit(1)

    return {"year": year, "outside": outside}


def write_header_to_csv(fileName):
    """
    Write header values to a .csv file
    """
    file = open(fileName, "w")
    writer = csv.writer(file, delimiter=",", lineterminator="\n")
    writer.writerow(OBSERVATIONATTRIBUES)
    file.close()


def main():
    args = parse_cmd_line()
    dict = get_observations(int(args["outside"]), args["year"])
    fileName = prepare_data_file(int(args["outside"]))
    write_observations(dict, fileName)
    # format_data.py script expects the file path to begin with 'data', not './data'
    sys.stdout.writelines(fileName[2:])
    exit(0)


if __name__ == "__main__":
    main()
