import os
import json
import argparse

from . import __author__, __about__, __version__

CURRENT_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(CURRENT_FILE_PATH, "data", "settings.json")


def usage():
    return """
    Usage
    =====
        torment mode --<option> <argument>


    Examples
    ========
            Open an onion url
            -----------------------
            torment open --url <onion_url>


            Search the darkweb
            --------------------
            torment --engine <search_engine_name> --query
    """


def create_parser():
    parser = argparse.ArgumentParser(
        description=f"tor2tor - by {__author__} | {__about__}",
        usage=usage(),
        epilog="Capture onion services on a given onion service.",
    )
    parser.add_argument("-u", "--url", help="onion url to scrape")
    parser.add_argument(
        "-l", "--limit", help="number of links to capture", type=int, default=10
    )
    parser.add_argument(
        "-o",
        "--open",
        help="open images after capturing",
        action="store_true",
    )
    parser.add_argument(
        "--headless", help="run firefox in headless mode", action="store_true"
    )
    parser.add_argument(
        "-t",
        "--tor",
        help="specify the path to the tor.exe binary (for windows systems)",
    )
    parser.add_argument("-v", "--version", version=__version__, action="version")
    return parser


def settings() -> dict:
    """
    Loads the program's settings from /data/settings.json

    :return: Dictionary (JSON) containing program settings
    """

    # Load the settings from the file
    with open(SETTINGS_PATH) as file:
        data = json.load(file)

    return data


def write_tor_path(data: dict):
    # Open the JSON file in write mode
    with open(SETTINGS_PATH, "w") as file:
        # Write the updated dictionary back to the file
        json.dump(data, file)


def update_tor_path(tor_path: str):
    data = settings()
    data["tor-path"] = tor_path.replace("\\", "/")
    write_tor_path(data=data)
    print(f"Updated Windows Tor binary path: {data}")
