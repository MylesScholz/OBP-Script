from __future__ import print_function
import os
import sys
import csv
import json
import requests


def test_import():
    print("col_functions.py test")


# 'Eval' functions are called from the merge_tables function to evaluate the
# contents of each column for the output spreadsheet. For each row in the
# original table, each eval function is called sequentially to construct the
# desired output row.

# I chose to encapsulate each column value in its own eval function to make
# the interpretation of input data as modular as possible. Each eval function
# uses potentially different logic to generate properly formatted output values,
# and each function can be modified independently.


def collector_name(in_file, user_name):
    # Open usernames CSV

    with open(in_file, "r", encoding="utf-8", errors="replace") as file:
        for row in file:
            # Remove trailing characters and split line into array

            row = row.rstrip("\r\n")

            row = row.split(",")

            # Found a match...

            if row[1] == user_name:
                # First name: 1st word of column 1

                first_name = row[0].split(" ")[0]

                # First letter of the first name

                first_initial = first_name[0] + "."

                # Last name: 2nd word of column 1

                last_name = row[0].split(" ")[1]

                # Done

                return first_name, first_initial, last_name

    return "", "", ""


def date_1(in_date):
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

        # Check input

        if in_date == "":
            return "", "", ""

        date = in_date.split("/")

        if len(date) > 1:
            day = date[1]

            month = month_numeral[int(date[0]) - 1]

            year = date[2]

        else:
            date = in_date.split("-")

            day = date[2]

            month = month_numeral[int(date[1]) - 1]

            year = date[0]

        return day, month, year

    except:
        return "", "", ""


def time_1(in_time):
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


def date_2(in_date):
    # According to Andony M. (email 5/3/2020), these are the possible formats:

    # 5/7/2019 16:45

    # 2019/04/28 7:10 PM UTC

    # 2019/06/03 12:00 PM PDT

    # 2019/06/30 7:52 AM HST

    # 2019-06-12T13:26:00-07:00

    # 21 Apr 2020 16:30:08 -0700

    # print('in_date 2:' + in_date)

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


def date_2_orig(in_date):
    # Check input

    if in_date == "":
        return "", "", "", ""

    # Init vars

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

    in_date = in_date.split("T")

    # print(in_date)

    # There are several input formats for this col

    # If the format can be split with T continue:

    if len(in_date) == 2:
        # print("Splitting with T...")

        in_date = in_date[0].split("-")

        # Parse values from full date string

        day = in_date[2]

        # Reference numeral array

        month = month_numeral[int(in_date[1]) - 1]

        # Year is straight forward

        year = in_date[0]

        # Calculate merge string

        merge = "-" + day + month

    else:
        # print("Splitting without T...")

        in_date = in_date[0].split(" ")

        in_date = in_date[0].split("/")

        # Check if month is in first or second location

        if int(in_date[1]) > 12:
            day = in_date[1]

            month = month_numeral[int(in_date[0]) - 1]

        else:
            day = in_date[0]

            month = month_numeral[int(in_date[1]) - 1]

        year = in_date[2]

        merge = "-" + day + month

    return day, month, year, merge


def time_2(in_time):
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


def time_2_orig(in_time):
    # Check input

    if in_time == "":
        return ""

    # Split full time string to remove date (1st word)

    in_time = in_time.split("T")

    if len(in_time) == 2:
        # print("Splitting with T...")

        in_time = in_time[1].split(":")

        in_time = in_time[0] + ":" + in_time[1]

    else:
        # print("Splitting without T...")

        in_time = in_time[0].split(" ")

        in_time = in_time[1]

    return in_time


def location_guess(address):
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


def round_coord(coord):
    temp = "%.4f" % (float(coord))

    if len(temp.split(".")[1]) < 4:
        print("coordinate didn't have 4 digits:", temp)

        temp = float(str(temp) + "0")

        print("fixed(?):", temp)

    return temp


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


def elevation(lat, long):
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
