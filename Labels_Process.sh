#!/bin/bash

# Change the current working directory to the directory where this script is located
cd "$(dirname "$0")"

# Run the pipeline in "labels only" mode
python3 full_pipeline.py --labels-only