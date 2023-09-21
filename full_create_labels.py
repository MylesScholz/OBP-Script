# Author: Myles Scholz
# Created on September 15, 2023
# Description: Module that creates bee specimen labels for new entries in the Oregon Bee Atlas database
import csv
import sys
import os

import textwrap as tw
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.image import BboxImage
from matplotlib.transforms import Bbox, TransformedBbox
from matplotlib.backends.backend_pdf import PdfPages
import treepoem as tp
import numpy as np
from tqdm import tqdm


# File Name Constants
LABELS_CONFIG_FILE = "config/labels_config.csv"

# PDF Layout Constants
LETTER_WIDTH = 8.5
LETTER_HEIGHT = 11

HORIZONTAL_MARGIN = 0.25
VERTICAL_MARGIN = 0.5

N_ROWS = 25
N_COLUMNS = 10

LABEL_WIDTH = 0.666
LABEL_HEIGHT = 0.311

# Calculate equal spacing between labels
HORIZONTAL_SPACING = (
    LETTER_WIDTH - (2 * HORIZONTAL_MARGIN) - (N_COLUMNS * LABEL_WIDTH)
) / (N_COLUMNS - 1)
VERTICAL_SPACING = (LETTER_HEIGHT - (2 * VERTICAL_MARGIN) - (N_ROWS * LABEL_HEIGHT)) / (
    N_ROWS - 1
)

# Label Layout Constants

# Theshold that text should not cross to avoid overlapping with data matrix
TEXT_CUTOFF = 0.466

# Object containing text box formatting and layout presets
TEXT_BOXES = {
    "location": {  # Collection Location
        "x_position": 0.005,
        "y_position": LABEL_HEIGHT - 0.005,
        "alignment": "top",
        "font_size": 4.5,
        "font_family": "Gill Sans MT Condensed",
        "font_style": "normal",
        "line_height": 0.8,
        "rotation": 0,
    },
    "date": {  # Collection Date
        "x_position": 0.005,
        "y_position": LABEL_HEIGHT - 0.175,
        "alignment": "top",
        "font_size": 6.3,
        "font_family": "Gill Sans MT Condensed",
        "font_style": "normal",
        "line_height": 0.8,
        "rotation": 0,
    },
    "name": {  # Collector Name
        "x_position": 0.005,
        "y_position": 0.005,
        "alignment": "bottom",
        "font_size": 4.5,
        "font_family": "Gill Sans MT",
        "font_style": "italic",
        "line_height": 0.8,
        "rotation": 0,
    },
    "method": {
        "x_position": LABEL_WIDTH - 0.275,
        "y_position": 0.005,
        "alignment": "bottom",
        "font_size": 4.5,
        "font_family": "Gill Sans MT",
        "font_style": "italic",
        "line_height": 0.8,
        "rotation": 0,
    },
    "number": {  # Observation No.
        "x_position": LABEL_WIDTH + 0.005,
        "y_position": 0.01,
        "alignment": "bottom",
        "font_size": 6,
        "font_family": "Gill Sans MT",
        "font_style": "normal",
        "line_height": 0.8,
        "rotation": 90,
    },
}

# Data matrix layout values
DATA_MATRIX = {
    "x_position": LABEL_WIDTH - 0.185,
    "y_position": 0.005,
    "width": 0.10,
}


# Column Name Constants

# Observation Number
OBSERVATION_NUMBER = "Observation No."

# Collector
FIRST_INITIAL = "Collector - First Initial"
LAST_NAME = "Collector - Last Name"

# IDs and Date
SAMPLE_ID = "Sample ID"
SPECIMEN_ID = "Specimen ID"
DAY = "Collection Day 1"
MONTH = "Month 1"
YEAR = "Year 1"

# Location
COUNTRY = "Country"
STATE = "State"
COUNTY = "County"
PLACE = "Abbreviated Location"
LATITUDE = "Dec. Lat."
LONGITUDE = "Dec. Long."
ELEVATION = "Elevation"

# Collection Method
METHOD = "Collection method"


def get_labels_config():
    # Read labels_config.csv to get the output file path and starting observation number
    with open(LABELS_CONFIG_FILE, newline="") as labels_config_file:
        labels_config = list(csv.DictReader(labels_config_file))[0]

    return labels_config


def run(dataset: list):
    print("Creating Labels")

    labels_config = get_labels_config()
    output_file_path = labels_config["Output File Path"]

    # Open a PDF file
    with PdfPages(output_file_path) as pdf:
        # Calculate partition values
        part_size = N_ROWS * N_COLUMNS
        n_parts = (len(dataset) // part_size) + 1
        part_start = 0
        part_end = part_size
        page_i = 1

        # Check that the partition end doesn't exceed the total length of the data
        if part_end > len(dataset):
            part_end = len(dataset)

        # Loop through the data, writing one page per partition
        while part_start < len(dataset):
            print("Page {}/{}".format(page_i, n_parts))
            write_pdf_page(pdf, dataset[part_start:part_end])

            # Increment the partition values
            part_start = part_end
            part_end += part_size
            if part_end > len(dataset):
                part_end = len(dataset)
            page_i += 1

    print("Creating Labels => Done")

    # TODO: logging
