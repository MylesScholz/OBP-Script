# Author: Myles Scholz
# Created on July 7, 2023
# Description: Takes formatted bee observation data and creates sheets of specimen labels

import sys
import os
import csv
import textwrap as tw
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.image import BboxImage
from matplotlib.transforms import Bbox, TransformedBbox
from matplotlib.backends.backend_pdf import PdfPages
import treepoem as tp
import numpy as np


# PDF Layout Constants
LETTER_WIDTH = 8.5
LETTER_HEIGHT = 11

HORIZONTAL_MARGIN = 0.25
VERTICAL_MARGIN = 0.5

N_ROWS = 25
N_COLUMNS = 10

LABEL_WIDTH = 0.666
LABEL_HEIGHT = 0.311

HORIZONTAL_SPACING = (
    LETTER_WIDTH - (2 * HORIZONTAL_MARGIN) - (N_COLUMNS * LABEL_WIDTH)
) / (N_COLUMNS - 1)
VERTICAL_SPACING = (LETTER_HEIGHT - (2 * VERTICAL_MARGIN) - (N_ROWS * LABEL_HEIGHT)) / (
    N_ROWS - 1
)

# Label Layout Constants

TEXT_CUTOFF = 0.466

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

DATA_MATRIX = {
    "x_position": LABEL_WIDTH - 0.185,
    "y_position": 0.005,
    "width": 0.10,
}


def parse_command_line():
    """
    Parses command line arguments, checking for --input and --output values
    """

    input_file_path = ""
    output_file_path = ""

    # Check for --input argument (required)
    if "--input" not in sys.argv:
        print("ERROR: --input argument not set")
        exit(1)

    # Parse command line arguments
    for i, arg in enumerate(sys.argv):
        if arg == "--input":
            if i + 1 > len(sys.argv):
                print("ERROR: --input argument not set")
                exit(1)
            input_file_path = sys.argv[i + 1]
        elif arg == "--output":
            if i + 1 > len(sys.argv):
                print("ERROR: --output argument not set")
                exit(1)
            output_file_path = sys.argv[i + 1]

    # If the output file path is unset, name it after the input file
    if output_file_path == "":
        input_file_directory, input_file = os.path.split(input_file_path)
        input_file_name, input_file_extension = os.path.splitext(input_file)
        output_file_path = input_file_name + ".pdf"

    # Check that input file path is a CSV file
    if not input_file_path.lower().endswith(".csv"):
        print("ERROR: input file must be in .csv format")
        exit(1)

    # Check that output file path is a PDF file
    if not output_file_path.lower().endswith(".pdf"):
        print("ERROR: output file must be in .pdf format")
        exit(1)

    # Check that input file exists
    if not os.path.isfile(input_file_path):
        print("ERROR: input file must exist")
        exit(1)

    return input_file_path, output_file_path


def add_text_box(figure, basis_x, basis_y, text, box_type):
    box_obj = TEXT_BOXES[box_type]

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

    # Resize text to cutoff
    r = figure.canvas.get_renderer()
    text_bbox = text.get_window_extent(renderer=r)
    while text_bbox.fully_containsx((TEXT_CUTOFF + basis_x) * figure.dpi):
        text.set_fontsize(text.get_fontsize() - 0.1)
        text_bbox = text.get_window_extent(renderer=r)


def add_data_matrix(figure, basis_x, basis_y, data):
    image = tp.generate_barcode(
        barcode_type="datamatrixrectangular",
        data=data,
        options={"version": "8x18"},
    )
    data_matrix = np.asarray(image)
    data_matrix = np.rot90(image)

    abs_x = basis_x + DATA_MATRIX["x_position"]
    abs_y = basis_y + DATA_MATRIX["y_position"]
    width = DATA_MATRIX["width"]
    height = (image.width / image.height) * width

    data_matrix_bbox = Bbox.from_bounds(abs_x, abs_y, width, height)
    data_matrix_bbox = TransformedBbox(data_matrix_bbox, figure.dpi_scale_trans)

    figure.add_artist(
        BboxImage(
            data_matrix_bbox,
            cmap="binary_r",
            interpolation="none",
            data=data_matrix,
            zorder=1000,
        )
    )


def write_pdf_page(pdf: PdfPages, data):
    # Create a matplotlib Figure
    figure = plt.figure(
        figsize=(LETTER_WIDTH, LETTER_HEIGHT), dpi=600, layout="constrained"
    )

    for i, entry in enumerate(data):
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
        if entry["Country"] == "USA":
            text_1 = "USA:{}:{} {} {} {} {}m".format(
                entry["State"],
                entry["County"],
                entry["Abbreviated Location"],
                entry["Dec. Lat."],
                entry["Dec. Long."],
                entry["Elevation"],
            )
        elif entry["Country"] == "Canada":
            text_1 = "CANADA:{} {} {} {} {}m".format(
                entry["State"],
                entry["Abbreviated Location"],
                entry["Dec. Lat."],
                entry["Dec. Long."],
                entry["Elevation"],
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
            entry["Collection Day 1"],
            entry["Month 1"],
            entry["Year 1"],
            entry["Sample ID"],
            entry["Specimen ID"],
        )
        add_text_box(figure, basis_x, basis_y, text_2, "date")

        # Text Box 3 (Collector and Method)
        text_3 = "{}{} {}".format(
            entry["Collector - First Initial"],
            entry["Collector - Last Name"],
            entry["Collection method"],
        )
        add_text_box(figure, basis_x, basis_y, text_3, "name")

        # Text Box 4 (Observation No.)
        text_4 = entry["Observation No."]
        add_text_box(figure, basis_x, basis_y, text_4, "number")

        # Barcode (Data Matrix of Observation No.)
        add_data_matrix(figure, basis_x, basis_y, text_4)

    # Save the figure to a new page of the PDF
    pdf.savefig(figure)


def main():
    input_file_path, output_file_path = parse_command_line()

    with open(input_file_path, newline="") as input_file:
        input_data = list(csv.DictReader(input_file))

    with PdfPages(output_file_path) as pdf:
        part_size = N_ROWS * N_COLUMNS
        part_start = 0
        part_end = part_size

        if part_end > len(input_data):
            part_end = len(input_data)

        while part_start < len(input_data):
            write_pdf_page(pdf, input_data[part_start:part_end])

            part_start = part_end
            part_end += part_size
            if part_end > len(input_data):
                part_end = len(input_data)


if __name__ == "__main__":
    main()
