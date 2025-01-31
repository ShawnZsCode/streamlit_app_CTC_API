"""Single Read File Function to save multiple definition."""

import json
import csv
import os


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


JSON_SETTINGS = read_file_json("session_manager\\Settings.json")


def directory_create(
    *,
    root: str = JSON_SETTINGS["files"]["chatHistoryCache"],
    folder: str = "",
) -> str:
    """Ensures a directory for cache of fetched files"""
    if folder == "":
        root_directory = root
    else:
        root_directory = f"{root}\\{folder}"
    try:
        if not os.path.isdir(root_directory):
            os.makedirs(root_directory, exist_ok=True)
        return root_directory
    except Exception as err:
        raise err


def write_file_json(
    *,
    stream: dict,
    file_name: str,
    folder: str = "",
) -> None:
    """Writes a json file from streamed data"""
    file_path = f"{directory_create(folder=folder)}"
    # os.makedirs(file_path, exist_ok=True)
    try:
        file_path += f"\\{file_name}.json"
        with open(file=file_path, mode="w") as f:
            # f.write(json.dumps(stream, indent=4))
            json.dump(stream, f, indent=4)
            # CTCLog(LOG_TITLE).info(f"Saved {file_path}")
    except Exception as err:
        raise err
        # CTCLog(LOG_TITLE).error(str(err))


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


# Prevent running from this file
if __name__ == "__main__":
    pass
