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
    # Read LABELS_CONFIG_FILE to get the output file path and starting and ending rows
    with open(LABELS_CONFIG_FILE, newline="") as labels_config_file:
        labels_config = list(csv.DictReader(labels_config_file))[0]

    return labels_config


def validate_starting_row(starting_row_entry: str, maximum: int):
    # Try to convert the starting row entry (from the config file) to an integer
    try:
        starting_row = int(starting_row_entry)

        # Check the valid bounds for a starting row
        if starting_row < 0 or starting_row > maximum:
            starting_row = 0
    except:
        # Return the first row index by default
        starting_row = 0

    return starting_row


def validate_ending_row(ending_row_entry: str, default: int, starting_row: int):
    # Try to convert the ending row entry (from the config file) to an integer
    try:
        ending_row = int(ending_row_entry)

        # Check the valid bounds for an ending row
        if ending_row < starting_row:
            ending_row = default
    except:
        # Return the given default value if unsuccessful
        ending_row = default

    return ending_row


def add_text_box(figure, basis_x, basis_y, text, box_type):
    """
    Adds a text box directly to the given figure (no plots used)
    """
    # Fetch the specified text box layout and formatting preset
    box_obj = TEXT_BOXES[box_type]

    # Add the text box
    text = figure.text(
        basis_x + box_obj["x_position"],
        basis_y + box_obj["y_position"],
        text,
        size=box_obj["font_size"],
        name=box_obj["font_family"],
        style=box_obj["font_style"],
        linespacing=box_obj["line_height"],
        ha="left",
        va=box_obj["alignment"],
        rotation=box_obj["rotation"],
        transform=figure.dpi_scale_trans,
        wrap=True,
    )

    # Resize text to fit left of the cutoff
    r = figure.canvas.get_renderer()
    text_bbox = text.get_window_extent(renderer=r)
    # Decrement font size until the cutoff no longer overlaps with the text box
    while text_bbox.fully_containsx((TEXT_CUTOFF + basis_x) * figure.dpi):
        text.set_fontsize(text.get_fontsize() - 0.1)
        text_bbox = text.get_window_extent(renderer=r)


def add_data_matrix(figure, basis_x, basis_y, data):
    """
    Generates and adds a rectangular (8 x 18) data matrix to the given figure
    """

    # Generate the data matrix using the Treepoem library (Python wrapper for BWIPP)
    image = tp.generate_barcode(
        barcode_type="datamatrixrectangular",
        data=data,
        options={"version": "8x18"},
    )
    # Convert the PIL Image object returned above into a Numpy array
    data_matrix = np.asarray(image)
    # Rotate the matrix 90 degrees anticlockwise
    data_matrix = np.rot90(image)

    # Calculate position of the bottom left corner of the data matrix relative
    # to the whole figure
    abs_x = basis_x + DATA_MATRIX["x_position"]
    abs_y = basis_y + DATA_MATRIX["y_position"]
    # Set the width to the specified value
    width = DATA_MATRIX["width"]
    # Calculate the height with the given width, maintaing the aspect ratio
    # The aspect ratio is inverted because "image" was not rotated
    height = (image.width / image.height) * width

    # Create a matplotlib bounding box and transform it from inches to pixels
    data_matrix_bbox = Bbox.from_bounds(abs_x, abs_y, width, height)
    data_matrix_bbox = TransformedBbox(data_matrix_bbox, figure.dpi_scale_trans)

    # Add the data matrix directly to the figuer as an image with a given bounding box
    figure.add_artist(
        BboxImage(
            data_matrix_bbox,
            cmap="binary_r",  # Greyscale colorscheme with high values being lighter
            interpolation="none",  # Avoid artifacts from resizing the image
            data=data_matrix,
            zorder=1000,  # Bring image to the front
        )
    )


def write_pdf_page(pdf: PdfPages, data):
    """
    Creates a PDF page of labels from a given list of data entries
    """

    # Create a matplotlib Figure
    figure = plt.figure(
        figsize=(LETTER_WIDTH, LETTER_HEIGHT), dpi=600, layout="constrained"
    )

    # Loop through the data entries
    for i, entry in tqdm(enumerate(data), desc="        Labels", total=len(data)):
        # Calculate the row and column of the current label
        row = N_ROWS - (i // N_COLUMNS) - 1
        column = i % N_COLUMNS

        # Calculate basis coordinates for the current label
        # Label text will be positioned relative to these coordinates
        basis_x = HORIZONTAL_MARGIN + (column * (LABEL_WIDTH + HORIZONTAL_SPACING))
        basis_y = VERTICAL_MARGIN + (row * (LABEL_HEIGHT + VERTICAL_SPACING))

        # Bounding rectangle to aid layout editing
        # rectangle = plt.Rectangle(
        #     (basis_x, basis_y),
        #     LABEL_WIDTH,
        #     LABEL_HEIGHT,
        #     fill=False,
        #     linewidth=0.5,
        #     transform=figure.dpi_scale_trans,
        # )
        # figure.add_artist(rectangle)

        # Text Box 1 (Location)
        # Different formats for the US and Canada
        if entry[COUNTRY] == "USA":
            text_1 = "USA:{}:{}Co {} {} {} {}m".format(
                entry[STATE],
                entry[COUNTY],
                entry[PLACE],
                entry[LATITUDE],
                entry[LONGITUDE],
                entry[ELEVATION],
            )
        elif entry[COUNTRY] == "CAN":
            text_1 = "CANADA:{} {} {} {} {}m".format(
                entry[STATE],
                entry[PLACE],
                round(float(entry[LATITUDE]), 3),
                round(float(entry[LONGITUDE]), 3),
                entry[ELEVATION],
            )
        text_1 = tw.fill(text_1, 22, max_lines=3)

        add_text_box(
            figure,
            basis_x,
            basis_y,
            text_1,
            "location",
        )

        # Text Box 2 (Date)
        text_2 = "{}.{}{}-{}.{}".format(
            entry[DAY],
            entry[MONTH],
            entry[YEAR],
            entry[SAMPLE_ID],
            entry[SPECIMEN_ID],
        )
        add_text_box(figure, basis_x, basis_y, text_2, "date")

        # Text Box 3 (Collector and Method)
        text_3 = "{}{} {}".format(
            entry[FIRST_INITIAL],
            entry[LAST_NAME],
            entry[METHOD],
        )
        add_text_box(figure, basis_x, basis_y, text_3, "name")

        # Text Box 4 (Observation No.)
        text_4 = entry[OBSERVATION_NUMBER]
        add_text_box(figure, basis_x, basis_y, text_4, "number")

        # Barcode (Data Matrix of Observation No.)
        add_data_matrix(figure, basis_x, basis_y, text_4)

    # Save the figure to a new page of the PDF
    pdf.savefig(figure)


def run(dataset: list):
    print("Creating Labels")

    # Read configuration file
    labels_config = get_labels_config()
    output_file_path = labels_config["Output File Path"]
    starting_row = validate_starting_row(labels_config["Starting Row"], len(dataset))
    ending_row = validate_ending_row(
        labels_config["Ending Row"], len(dataset), starting_row
    )

    # Truncate dataset to create labels only from the given starting row to the ending row
    dataset = dataset[starting_row:ending_row]

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
            print("    Page {}/{}".format(page_i, n_parts))
            write_pdf_page(pdf, dataset[part_start:part_end])

            # Increment the partition values
            part_start = part_end
            part_end += part_size
            if part_end > len(dataset):
                part_end = len(dataset)
            page_i += 1

    print("Creating Labels => Done")

    # TODO: logging
