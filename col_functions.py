from __future__ import print_function
import os
import sys
import csv
import json
import requests


# 'Eval' functions are called from the merge_tables function to evaluate the
# contents of each column for the output spreadsheet. For each row in the
# original table, each eval function is called sequentially to construct the
# desired output row.

# I chose to encapsulate each column value in its own eval function to make
# the interpretation of input data as modular as possible. Each eval function
# uses potentially different logic to generate properly formatted output values,
# and each function can be modified independently.


def format_user_name(user_login: str, user_full_name: str):
    user_first_name = user_first_initial = user_last_name = ""

    if user_full_name != "":
        user_full_name_split = user_full_name.split(" ")

        # User first name assumed to be the first space-separated word in their full name
        # This will not capture middle names or compound first names (e.g., Mary Jo)
        user_first_name = user_full_name_split[0]
        user_first_initial = user_first_name[0] + "."

        # User last name assumed to be the last space-separated word in their full name
        # This will not capture middle names or compound last names (e.g., van Horn)
        # If there is only one name provided, the last name will be empty
        if len(user_full_name_split) > 1:
            user_last_name = user_full_name_split[-1]
    else:
        # user_full_name not provided in pulled data, so check usernames.csv
        with open(
            "data/usernames.csv", "r", encoding="utf-8", errors="replace"
        ) as file:
            for row in file:
                # Remove trailing characters and split line into array
                row = row.rstrip("\r\n")
                row = row.split(",")

                if row[1] == user_login:
                    user_full_name_split = row[0].split(" ")
                    # User first name has caveats as above
                    user_first_name = user_full_name_split[0]
                    user_first_initial = user_first_name[0] + "."

                    # User last name has caveats as above
                    user_last_name = user_full_name_split[-1]

    return user_first_name, user_first_initial, user_last_name


def format_date_1(input_date):
    # Check input
    if input_date == "":
        return "", "", ""

    try:
        month_numeral = [
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

        date = input_date.split("/")
        if len(date) > 1:
            day = date[1]
            month = month_numeral[int(date[0]) - 1]
            year = date[2]
        else:
            date = input_date.split("-")
            day = date[2]
            month = month_numeral[int(date[1]) - 1]
            year = date[0]

        return day, month, year
    except:
        return "", "", ""


def format_time_1(in_time):
    # Check input
    if in_time == "":
        return ""

    # Split full time string to remove date (1st word)
    in_time = in_time.split(" ")

    # Split time word by : to separate hours, mins, secs
    return_time = in_time[1].split(":")

    # Convert from UTC to PST by -7
    if (int(return_time[0]) - 7) < 6:
        return_time[0] = str(int(return_time[0]) + 24 - 7)

    else:
        return_time[0] = str(int(return_time[0]) - 7)

    # Reattach the hours and minutes, leaving out seconds
    return_time = return_time[0] + ":" + return_time[1]

    return return_time


def format_date_2(in_date):
    # According to Andony M. (email 5/3/2020), these are the possible formats:
    #
    # 5/7/2019 16:45
    # 2019/04/28 7:10 PM UTC
    # 2019/06/03 12:00 PM PDT
    # 2019/06/30 7:52 AM HST
    # 2019-06-12T13:26:00-07:00
    # 21 Apr 2020 16:30:08 -0700

    month_numeral = [
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

    # months = ['January','February','March','April','May','June','July','August','September','October','November','December']

    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    # Check input

    if in_date == "" or in_date is None:
        return "", "", "", ""

    # # If the string contains 'T' it is a differently formatted date time value

    # if 'T' in in_date:

    #     print("Found different format:",in_date)

    # Start with 2019-06-12T13:26:00-07:00 format

    date = in_date.split(" ")

    if len(date) < 2:
        date_time = in_date.split("T")

        if len(date_time) == 2:
            date = date_time[0]

            date = date.split("-")

            day = date[2]

            # month = date[1]

            month = month_numeral[int(date[1]) - 1]

            year = date[0]

            merge = "-" + day + month

            return day, month, year, merge

        else:
            return "", "", "", ""

    # Check if date was parsed into different format

    for index, curr_month in enumerate(months):
        # if curr_month in in_date:

        if in_date.find(curr_month) > 1:
            # print("Found written format:",curr_month," | ",in_date)

            date = in_date.split(" ")

            print("split date:", date)

            day = date[0]

            month = month_numeral[index]

            year = date[2]

            merge = "-" + day + month

            return day, month, year, merge

    # If the string can be split in two, it is formatted: 'mm/dd/yy hh:mm'

    # date[0] is the date, date[1] is the time

    date = in_date.split(" ")

    print("split date:", date)

    if len(date) == 2:
        # should be "5/7/2019 16:45" format

        date = date[0].split("/")

        day = date[1]

        month = month_numeral[int(date[0]) - 1]

        year = date[2]

    else:
        date = date[0].split("/")

        day = date[2]

        month = month_numeral[int(date[1]) - 1]

        year = date[0]

    merge = "-" + day + month

    return day, month, year, merge


def format_time_2(in_time):
    # According to Andony M. (email 5/3/2020), these are the possible formats:

    # 5/7/2019 16:45

    # 2019/04/28 7:10 PM UTC

    # 2019/06/03 12:00 PM PDT

    # 2019/06/30 7:52 AM HST

    # 2019-06-12T13:26:00-07:00

    # 21 Apr 2020 16:30:08 -0700

    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    # print('in_time 2:' + in_time)

    # Check input

    if in_time == "" or in_time is None:
        return ""

    # Start with 2019-06-12T13:26:00-07:00 format

    time = in_time.split(" ")

    if len(time) < 2:
        date_time = in_time.split("T")

        if len(date_time) == 2:
            time = date_time[1]

            time = time.split("-")

            return time[0]

        else:
            return ""

    # Check if date was parsed into different format

    for index, curr_month in enumerate(months):
        # if curr_month in in_date:

        if in_time.find(curr_month) > 1:
            time = in_time.split(" ")

            return time[3]

    # If the string can be split in two, it is formatted: 'mm/dd/yy hh:mm'

    # date[0] is the date, date[1] is the time

    time = in_time.split(" ")

    if len(time) == 2:
        # should be "5/7/2019 16:45" format

        return time[1]

    elif len(time) == 4:
        returnTime = ""

        if time[2] == "PM":
            reformattedTime = time[1].split(":")

            hour = int(reformattedTime[0])

            if hour < 12:
                hour = hour + 12

            minute = reformattedTime[1]

            returnTime = str(hour) + ":" + minute

        else:
            returnTime = time[1]

        return returnTime

    # # Check input

    # if in_time == '' or in_time is None:

    #     return ''

    # # If the string can be split in two, it is formatted: 'mm/dd/yy hh:mm'

    # # in_time[0] is the date, in_time[1] is the time

    # in_time = in_time.split(' ')

    # if len(in_time) == 2:

    #     in_time = in_time[1]

    #     in_time = in_time[0] + ":" + in_time[1]

    # #else:

    # #    in_time = in_time[0].split(' ')

    # #    in_time = in_time[1]

    # return in_time


def format_country(country_name: str):
    country_abbreviation = country_name

    if country_name == "United States":
        country_abbreviation = "USA"

    # Insert other known abbreviations here

    return country_abbreviation


def format_state(state_name: str):
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


def format_location_guess(address):
    """
    location_guess modifies the string from the place_guess column, transforming it into a more useful format.

    :param address: place_guess address value
    """
    address = address.split(", ")
    # If 'normal' address, should split in 3
    if len(address) == 3:
        # Correct address should have either "SS" or "SS xxxxx" form for the state.
        # SS represent a valid state initial
        # (xxxxx) represent a valid zipcode

        if len(address[2]) or (len(address[1]) == 8 and address[1][3:].isdigit()):
            # Check if the address includes 'county' and only return it if not
            if not (address[0][-7:].lower() == " county"):
                return address[0]
    return ""


def specimen_id(specimen_id_str):
    if specimen_id_str is None:
        return " "

    if specimen_id_str != "":
        if specimen_id_str[0].isalpha():
            return "NOT INT"

        else:
            return specimen_id_str


def format_coordinate(coordinate):
    if coordinate is None or coordinate == "":
        return ""

    return "{:.4f}".format(float(coordinate))


def write_elevation_res(elevation_file, lat, long, elevation):
    lat_rounded = "%.2f" % (float(lat))

    long_rounded = "%.2f" % (float(long))

    line_to_print = str(lat_rounded), str(long_rounded), str(elevation)

    # New System:

    # Check if file has been created: Elevations/input_file_elevation.csv

    # Write file or Append file based on this

    if not os.path.exists(elevation_file):
        with open(elevation_file, "w") as file:
            # file.write(line_to_print)

            writer = csv.writer(file)

            writer.writerow(line_to_print)

    else:
        with open(elevation_file, "a") as file:
            writer = csv.writer(file)

            writer.writerow(line_to_print)

    # Old System:

    # Always append results to same master file

    # with open(elevation_file, 'a') as f:

    #    writer = csv.writer(f)

    #    writer.writerow(line_to_print)


def read_elevation_csv(elevation_file, lat, long):
    # Create more matches by simplifying coordinates

    # print(lat,long)

    lat_rounded = "%.2f" % (float(lat))

    long_rounded = "%.2f" % (float(long))

    with open(elevation_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")

        for row in csv_reader:
            if (
                len(row) > 1
                and str(row[0]) == lat_rounded
                and str(row[1]) == long_rounded
            ):
                return row[2]

    return ""


def format_elevation(lat, long):
    """
    Checks for elevation based on the 'data/elevations.csv' reference file.
    New reference entries are no longer added, as they were previously generated
    by the Bing Maps API (now removed from this script), but can be input manually.

    :param lat: latitude to find the elevation
    :param long: longitude to find the elevation
    """

    # Establish Variables & Files
    elevation_file_name = "data/elevations.csv"

    # Check if the current lat and long have already been calculated
    csv_result = read_elevation_csv(elevation_file_name, lat, long)
    if csv_result != "":
        # A matching set of coordinates was found in results
        return int(float(csv_result))
    return 0


def collection(in_method):
    in_method_array = in_method.split(" ")

    if len(in_method_array) > 1:
        if in_method_array[0] == "blue":
            return "vane"

        else:
            return in_method_array[0]

    else:
        return in_method
