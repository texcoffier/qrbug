#!/bin/sh
# Gets the wanted name of the virtual environment
VENV_FOLDER=".venv/"
if [ -n "$1" ]; then
	VENV_FOLDER="$1"
fi
echo "Creating new virtual environment at '$VENV_FOLDER'"

# Creates a new virtual environment if the virtual environment does not exist
if [ ! -d VENV_FOLDER ]; then
	python3 -m venv "$VENV_FOLDER"
	echo "New virtual environment created !"
fi

# Selects the current virtual environment
. "$VENV_FOLDER/bin/activate"

# Installs the package in editable mode
echo "Installing or updating package into virtual environment..."
python3 -m pip install -e .
if [ $? -eq 0 ]; then
	echo "Package and software installed, ready to develop or run !"
else
	echo "Something went wrong..."
fi

# Creating the logs folders
mkdir LOGS LOGS/MAIL LOGS/ERROR 2>/dev/null