# Author: Myles Scholz
# Created on July 7, 2023
# Description: Takes formatted bee observation data and creates sheets of specimen labels

import sys
import matplotlib as mpl
import matplotlib.pyplot as plt
import textwrap

# PDF Layout Constants
LETTER_WIDTH = 8.5
LETTER_HEIGHT = 11

HORIZONTAL_MARGIN = 0.25
VERTICAL_MARGIN = 0.5

N_ROWS = 25
N_COLUMNS = 10

LABEL_WIDTH = 0.666
LABEL_HEIGHT = 0.311

HORIZONTAL_SPACING = 0.1488888889
VERTICAL_SPACING = 0.0927083333

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

# TODO: Barcode


def parse_command_line():
    pass


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


def main():
    # TODO: Read and partition data

    figure = plt.figure(figsize=(LETTER_WIDTH, LETTER_HEIGHT), layout="constrained")

    for i in range(N_ROWS):
        for j in range(N_COLUMNS):
            # Calculate basis coordinates for the current label
            # Label text will be positioned relative to these coordinates
            basis_x = HORIZONTAL_MARGIN + (j * (LABEL_WIDTH + HORIZONTAL_SPACING))
            basis_y = VERTICAL_MARGIN + (i * (LABEL_HEIGHT + VERTICAL_SPACING))

            # TODO: Remove rectangle when done with layout
            rectangle = plt.Rectangle(
                (basis_x, basis_y),
                LABEL_WIDTH,
                LABEL_HEIGHT,
                transform=figure.dpi_scale_trans,
            )
            figure.add_artist(rectangle)

            add_text_box(
                figure,
                basis_x,
                basis_y,
                textwrap.fill(
                    "USA:OR:KlamathCo Keno 42.139 -122.018 1179m", 22, max_lines=3
                ),
                "location",
            )
            add_text_box(figure, basis_x, basis_y, "3.VII2023-1.1", "date")
            add_text_box(
                figure, basis_x, basis_y, "M. and D.O'Loughlin vane trap", "name"
            )
            # add_text_box(figure, basis_x, basis_y, "vane trap", "method")
            add_text_box(figure, basis_x, basis_y, "2300537", "number")

    plt.savefig("test.pdf")
    # plt.show()


if __name__ == "__main__":
    main()
