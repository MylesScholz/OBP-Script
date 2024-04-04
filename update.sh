#!/bin/bash

# Change the current working directory to the directory where this script is located
cd "$(dirname "$0")"

# Fetch the latest changes from the remote
git fetch origin

# Reset the local repository to origin/main
git reset --hard origin/main