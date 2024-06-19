# Author: Myles Scholz
# Created on September 15, 2023
# Description: Module that creates bee specimen labels for new entries in the Oregon Bee Atlas database
import csv
import datetime
import os
import traceback
import tkinter as tk
from tkinter import filedialog

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
LOG_FILE = "log_file.txt"

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
        "font_file": "fonts/Gill Sans MT Condensed.ttf",
        "line_height": 1.0,
        "rotation": 0,
        "cutoff_point": (TEXT_CUTOFF, LABEL_HEIGHT - 0.175),
    },
    "date": {  # Collection Date
        "x_position": 0.005,
        "y_position": LABEL_HEIGHT - 0.175,
        "alignment": "top",
        "font_size": 6.3,
        "font_file": "fonts/Gill Sans MT Condensed.ttf",
        "line_height": 1.0,
        "rotation": 0,
        "cutoff_point": (TEXT_CUTOFF, 0.065),
    },
    "name": {  # Collector Name
        "x_position": 0.005,
        "y_position": 0.005,
        "alignment": "bottom",
        "font_size": 4.5,
        "font_file": "fonts/Gill Sans MT.ttf",
        "line_height": 1.0,
        "rotation": 0,
        "cutoff_point": (TEXT_CUTOFF, 0),
    },
    "method": {
        "x_position": LABEL_WIDTH - 0.275,
        "y_position": 0.005,
        "alignment": "bottom",
        "font_size": 4.5,
        "font_file": "fonts/Gill Sans MT Italic.ttf",
        "line_height": 1.0,
        "rotation": 0,
        "cutoff_point": (TEXT_CUTOFF, 0),
    },
    "number": {  # Observation No.
        "x_position": LABEL_WIDTH + 0.005,
        "y_position": 0.01,
        "alignment": "bottom",
        "font_size": 6,
        "font_file": "fonts/Gill Sans MT.ttf",
        "line_height": 1.0,
        "rotation": 90,
        "cutoff_point": (0, 0),
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


def write_labels_config(labels_config):
    # Open LABELS_CONFIG_FILE to write updated output file path
    labels_config_header = ["Output File Path", "Starting Row"]
    with open(LABELS_CONFIG_FILE, "w", newline="") as labels_config_file:
        csv_writer = csv.DictWriter(labels_config_file, fieldnames=labels_config_header)
        csv_writer.writeheader()
        csv_writer.writerow(labels_config)


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


def get_starting_row(init_starting_row: int, data_length: int):
    """
    Gets a valid starting row from the user, defaulting to the one provided in the config file
    """

    # Notify the user of the default value
    # Use 1-indexing when communicating with the user because it is more intuitive
    print(
        "    Enter a starting row (1-indexed, inclusive). Default value:",
        init_starting_row + 1,
        "(new entries).",
    )

    # Loop until a valid response is given
    valid = False
    while not valid:
        # Prompt the user
        starting_row_response = input("    Starting Row: ")

        # Try to convert the user's response to an int
        try:
            starting_row_output = int(starting_row_response)

            # Check the valid bounds
            if starting_row_output > 0 and starting_row_output <= data_length:
                # Escape the loop if within the bounds
                valid = True
            else:
                print("    Invalid starting row.\n")
        except:
            # If unable to convert the users response to an int,
            # check whether the response was empty
            if starting_row_response == "":
                # The user's response was empty, so use the default value
                # and escape the loop
                starting_row_output = init_starting_row + 1
                valid = True
            else:
                print("    Invalid response.\n")

    # Notify the user of the selected starting row
    # This may not be obvious if they selected the default value
    print("    Selected Starting Row: {}\n".format(starting_row_output))

    # Return the selected value, converting back to 0-indexing
    return starting_row_output - 1


def get_ending_row(starting_row: int, data_length: int):
    """
    Gets a valid ending row from the user, defaulting to the last entry
    """

    # Notify the user of the default value
    # Use 1-indexing when communicating with the user because it is more intuitive
    # Use an inclusive range when communicating with the user because it is more intuitive
    print(
        "    Enter an ending row (1-indexed, inclusive). Default value:",
        data_length,
        "(last entry).",
    )

    # Loop until a valid response is given
    valid = False
    while not valid:
        # Prompt the user
        ending_row_response = input("    Ending Row: ")

        # Try to convert the user's response to an int
        try:
            ending_row_output = int(ending_row_response)

            # Check the valid bounds
            if ending_row_output > starting_row and ending_row_output <= data_length:
                # Escape the loop if within the bounds
                valid = True
            else:
                print("    Invalid ending row.\n")
        except:
            # If unable to convert the users response to an int,
            # check whether the response was empty
            if ending_row_response == "":
                # The user's response was empty, so use the default value
                # and escape the loop
                ending_row_output = data_length
                valid = True
            else:
                print("    Invalid response.\n")

    # Notify the user of the selected starting row
    # This may not be obvious if they selected the default value
    print("    Selected Ending Row: {}\n".format(ending_row_output))

    # Return the selected value
    return ending_row_output


def confirm_row_range(init_starting_row: int, data_length: int):
    # Get a starting and ending row from the user
    starting_row = get_starting_row(init_starting_row, data_length)
    ending_row = get_ending_row(starting_row, data_length)

    # Return validated responses
    return starting_row, ending_row


def add_text_box(figure, basis_x, basis_y, text, box_type):
    """
    Adds a text box directly to the given figure (no plots used)
    """
    # Fetch the specified text box layout and formatting preset
    box_obj = TEXT_BOXES[box_type]

    font_properties = mpl.font_manager.FontProperties(fname=box_obj["font_file"])

    # Add the text box
    text = figure.text(
        basis_x + box_obj["x_position"],
        basis_y + box_obj["y_position"],
        text,
        size=box_obj["font_size"],
        font_properties=font_properties,
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
    cutoff_point = (
        (box_obj["cutoff_point"][0] + basis_x) * figure.dpi,
        (box_obj["cutoff_point"][1] + basis_y) * figure.dpi,
    )

    # Debug print out for layout editing
    # print(
    #     box_type,
    #     "extents:",
    #     (
    #         (text_bbox.extents[0] / figure.dpi) - basis_x,
    #         (text_bbox.extents[1] / figure.dpi) - basis_y,
    #         (text_bbox.extents[2] / figure.dpi) - basis_x,
    #         (text_bbox.extents[3] / figure.dpi) - basis_y,
    #     ),
    # )

    while text.get_fontsize() > 1 and (
        text_bbox.containsx(cutoff_point[0]) or text_bbox.containsy(cutoff_point[1])
    ):
        text.set_fontsize(text.get_fontsize() - 0.1)
        text_bbox = text.get_window_extent(renderer=r)


def add_data_matrix(figure, basis_x, basis_y, data):
    """
    Generates and adds a rectangular (8 x 18) data matrix to the given figure
    """

    if data is None or data == "":
        return

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
            text_1 = "USA:{}:{}Co {} {:.3f} {:.3f} {}m".format(
                entry[STATE],
                entry[COUNTY],
                entry[PLACE],
                round(float(entry[LATITUDE]), 3),
                round(float(entry[LONGITUDE]), 3),
                entry[ELEVATION],
            )
        elif entry[COUNTRY] == "CAN":
            text_1 = "CANADA:{} {} {:.3f} {:.3f} {}m".format(
                entry[STATE],
                entry[PLACE],
                round(float(entry[LATITUDE]), 3),
                round(float(entry[LONGITUDE]), 3),
                entry[ELEVATION],
            )
        text_1 = tw.fill(text_1, 22)

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
    try:
        print("Creating Labels...")

        # Read configuration file
        labels_config = get_labels_config()
        output_file_path = os.path.relpath(labels_config["Output File Path"])
        starting_row = validate_starting_row(
            labels_config["Starting Row"], len(dataset)
        )

        root = tk.Tk()
        root.attributes("-alpha", 0.0)
        root.attributes("-topmost", True)

        if output_file_path.lower() == "select":
            output_file_path = filedialog.asksaveasfilename(
                initialdir="../", filetypes=[("PDF Files", "*.pdf")]
            )
            labels_config["Output File Path"] = os.path.relpath(output_file_path)
            write_labels_config(labels_config)

        # Confirm the range of rows to create labels from
        starting_row, ending_row = confirm_row_range(starting_row, len(dataset))

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

        root.destroy()

        # Log a success
        current_date = datetime.datetime.now()
        date_str = current_date.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as log_file:
            log_file.write(
                "{}: SUCCESS - Created labels at '{}' from new data\n".format(
                    date_str, output_file_path
                )
            )
            log_file.write("\n")

    except Exception:
        # Log the error
        current_date = datetime.datetime.now()
        date_str = current_date.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as log_file:
            log_file.write("{}: ERROR while creating labels:\n".format(date_str))
            log_file.write(traceback.format_exc())
            log_file.write("\n")

        input(
            "An error occurred while creating labels. Check {} for details.".format(
                LOG_FILE
            )
        )
        exit(1)
