import os
import json
import logging
import argparse

from rich.logging import RichHandler

from . import __author__, __about__, __version__

CURRENT_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(CURRENT_FILE_PATH, "data", "data.json")


def usage():
    return """
    Basic Usage
    ===========
        tor2tor --url http://example.onion


    Other Examples
    ==============
            Configure the tor.exe binary (for Windows systems)
            --------------------------------------------------
            tor2tor --tor C:\\path\\to\\tor.exe


            Run with headless Firefox
            -------------------------
            tor2tor --headless --url http://example.onion
            
            
            Open each image on capture
            --------------------------
            tor2tor --open --url http://example.onion
    """


def create_parser():
    parser = argparse.ArgumentParser(
        description=f"tor2tor - by {__author__} | {__about__}",
        usage=usage(),
        epilog="Capture screenshots of onion services on an onion service.",
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
    parser.add_argument(
        "-d", "--debug", help="run program in debug mode", action="store_true"
    )
    parser.add_argument("-v", "--version", version=__version__, action="version")
    return parser


def set_loglevel(debug_mode: bool) -> logging.getLogger:
    """
    Configure and return a logging object with the specified log level.

    :param debug_mode: If True, the log level is set to "NOTSET". Otherwise, it is set to "INFO".
    :return: A logging object configured with the specified log level.
    """
    logging.basicConfig(
        level="NOTSET" if debug_mode else "INFO",
        format="%(message)s",
        handlers=[
            RichHandler(markup=True, log_time_format="[%I:%M:%S %p]", show_level=False)
        ],
    )
    return logging.getLogger("Tor2Tor")


def load_data() -> dict:
    """
    Loads the program's data from /data/data.json

    :return: Dictionary (JSON) containing program settings
    """
    # Load the settings from the file
    with open(DATA_PATH) as file:
        data = json.load(file)

    return data


def write_tor_path(data: dict):
    """
    Writes path of the tor binary to data.json.

    :param data: The data to write to the data file.
    """
    # Open the JSON file in write mode
    with open(DATA_PATH, "w") as file:
        # Write the updated dictionary back to the file
        json.dump(data, file)


def update_tor_path(tor_path: str):
    """
    Updates the tor binary in the data file.

    :param tor_path: Path of the tor binary.
    """
    data = load_data()
    data["tor-path"] = tor_path.replace("\\", "/")
    write_tor_path(data=data)
    log.info(f"tor.exe path updated: {data}")


# Parse command-line arguments
args = create_parser().parse_args()
log = set_loglevel(debug_mode=args.debug)
