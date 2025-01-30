"""Single Read File Function to save multiple definition."""

import json
import csv


def read_file_json(path):
    """Simple Function to open, read and close a file
    Returns the contents of a json file"""
    try:
        with open(path, "r") as open_file:
            contents = json.loads(open_file.read())
    except Exception as err:
        print(err)
        contents = {"": {"": {"": ""}}}
    return contents


def read_file_csv(path):
    """Simple Function to open, read and close a file
    Returns the contents of a csv file"""
    try:
        with open(path, "r") as open_file:
            contents = csv.DictReader(open_file)
    except Exception as err:
        print(err)
        contents = ""
    return contents
