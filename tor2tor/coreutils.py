import os
import re
import time
import json
import random
import logging
import argparse
import subprocess
from datetime import datetime
from urllib.parse import urlparse

import requests
from rich import print
from rich.table import Table
from rich.markdown import Markdown
from rich.logging import RichHandler

from . import __author__, __about__, __version__

# Construct path to the user's home directory
PROGRAM_DIRECTORY = os.path.expanduser(os.path.join("~", "tor2tor"))


def settings() -> dict:
    """
    Loads settings from /settings/settings.json

    :return: Dictionary (JSON) containing settings
    """
    # Get the absolute path of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the settings.json file
    settings_path = os.path.join(current_dir, "settings", "settings.json")

    # Load the settings from the file
    with open(settings_path) as file:
        data = json.load(file)

    return data


def usage():
    return """
    tor2tor http://example.onion
    
    docker run --tty --volume rly0nheart/tor2tor http://example.onion
    """


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=f"tor2tor - by {__author__} | {__about__}",
        usage=usage(),
        epilog="Capture screenshots of onion services on an onion service.",
    )
    parser.add_argument("onion", help="onion url to scrape")
    parser.add_argument(
        "--headless",
        help="run Firefox WebDriver instances in headless mode",
        action="store_true",
    )
    parser.add_argument(
        "-l", "--limit", help="number of onion links to capture", type=int, default=10
    )
    parser.add_argument(
        "-p",
        "--pool",
        help="size of the Firefox WebDriver instance pool (default: %(default)s)",
        type=int,
        default=3,
    )
    parser.add_argument(
        "-t",
        "--threads",
        help="number of worker threads to run (default: %(default)s)",
        type=int,
        default=3,
    )
    parser.add_argument(
        "--log-skipped",
        help="log skipped onions on output",
        dest="log_skipped",
        action="store_true",
    )
    parser.add_argument(
        "-d", "--debug", help="run program in debug mode", action="store_true"
    )
    parser.add_argument("-v", "--version", version=__version__, action="version")
    return parser


def show_banner():
    """
    Prints a random banner from a list of 2 banners.
    """
    banners = [
        f"""
┌┬┐┌─┐┬─┐┌─┐┌┬┐┌─┐┬─┐
 │ │ │├┬┘┌─┘ │ │ │├┬┘
 ┴ └─┘┴└─└─┘ ┴ └─┘┴└─ {__version__}""",
        f"""
┌┬┐┌─┐┌┬┐
 │ ┌─┘ │ 
 ┴ └─┘ ┴ {__version__}""",
    ]

    print(random.choice(banners))


def set_loglevel(debug_mode: bool) -> logging.getLogger:
    """
    Configure and return a logging object with the specified log level.

    :param debug_mode: If True, the log level is set to "NOTSET". Otherwise, it is set to "INFO".
    :return: A logging object configured with the specified log level.
    """
    logging.basicConfig(
        level="NOTSET" if debug_mode else "INFO",
        format="%(levelname)s %(message)s",
        handlers=[
            RichHandler(markup=True, log_time_format="%H:%M:%S", show_level=False)
        ],
    )
    return logging.getLogger("Tor2Tor")


def add_http_to_link(link: str) -> str:
    """
    Adds 'http://' to the URL if it doesn't already start with 'http://' or 'https://'.

    :param link: The link to modify.
    :return: The modified URL.
    """
    if not link.startswith(("http://", "https://")):
        return f"http://{link}"
    return link


def is_valid_onion(url: str) -> bool:
    """
    Uses a regex pattern to determine whether a given url is an onion service or not.

    :param url: The url to check.
    :return: True if the url matches the strict pattern criterion. False if it doesn't

    Regex Explanation
    -----------------
    - ^ - Asserts the start of a string.
    - (http://|https://)? - Matches HTTP or HTTPS protocol in the string (optional).
    - (www\\.)? - Optionally matches the www. subdomain.
    - ([a-z2-7]{54,}d) - Matches 55 or more characters, where each can be a lowercase letter or a digit from 2 to 7,
      and ends with 'd'.
    - \\.onion - Matches .onion.
    - (/|$) - Matches either a forward slash or the end of the string.
    """
    if re.search(r"^(http://|https://)?(www\.)?([a-z2-7]{54,}d)\.onion(/|$)", url):
        return True
    else:
        return False


def create_table(table_headers: list, table_title: str = "") -> Table:
    """
    Creates a rich table with the given column headers.

    :param table_headers: The column headers to add to the Table.
    :param table_title: The title of the table (an empty string is the default tile).
    :returns: A table with added column headers.
    """
    table = Table(
        title=table_title,
        title_style="italic",
        caption=f"{time.asctime()}",
        caption_style="italic",
        show_header=True,
        header_style="bold",
        highlight=True,
    )
    for header in table_headers:
        table.add_column(header, style="dim" if header == "#" else "")
    return table


def construct_output_name(url: str) -> str:
    """
    Constructs an output name based on the network location part (netloc) of a given URL.

    :param url: The URL to parse.
    :return: The network location part (netloc) of the URL.
    """
    parsed_url = urlparse(url)
    output_name = parsed_url.netloc
    return output_name


def path_finder(url: str):
    """
    Checks if the specified directories exist.
    If not, it creates them.
    """
    os.makedirs(
        os.path.join(PROGRAM_DIRECTORY, construct_output_name(url=url)), exist_ok=True
    )


def convert_timestamp_to_datetime(timestamp: float) -> datetime:
    """
    Converts a Unix timestamp to a datetime object.

    :param timestamp: The Unix timestamp to be converted, given as a float.
    :return: A datetime object.
    """
    datetime_from_timestamp = datetime.fromtimestamp(timestamp)
    return datetime_from_timestamp


def get_file_info(filename: str) -> tuple:
    """
    Gets a given file's information.

    :param filename: File to get info for.
    :return: A tuple containing the file's size and created time.
    """
    file_size = os.path.getsize(filename=filename)

    created_time = convert_timestamp_to_datetime(
        timestamp=os.path.getmtime(filename=filename)
    )

    return file_size, created_time


def check_updates():
    """
    Checks the program's updates by comparing the current program version tag with the remote version tag from GitHub.
    """
    response = requests.get(
        "https://api.github.com/repos/rly0nheart/tor2tor/releases/latest"
    ).json()
    remote_version = response.get("tag_name")

    if remote_version != __version__:
        log.info(
            f"Tor2Tor version {remote_version} published at {response.get('published_at')} "
            f"is available. Run the 'update.sh' "
            f"script (for local installation) or re-pull the image (for docker container) "
            f"with 'docker pull rly0nheart/tor2tor' to get the updates. "
        )
        release_notes = Markdown(response.get("body"))
        print(release_notes)
        print("\n")


def tor_service(command: str):
    """
    Starts/Stops the Tor service based on the provided command and operating system.

    This function can start or stop the Tor service on Windows and Unix-like
    systems. On Windows, it looks for Tor\\tor\\tor.exe in the user's home directory.

    :param command: The command to manage the Tor service. Acceptable values are "start" or "stop".
    :raise: subprocess.CalledProcessError If the subprocess fails to execute.
    """

    if command not in ["start", "stop"]:
        log.warning("Command must be either 'start' or 'stop'")

    try:
        if os.name == "nt":
            tor_path = os.path.join(PROGRAM_DIRECTORY, settings().get("tor.exe"))

            if command == "start":
                log.info(f"Starting {tor_path}...")
                subprocess.Popen(tor_path)
            else:
                subprocess.Popen("taskkill /IM tor.exe /F")

        else:
            subprocess.run(["service", "tor", command])

    except subprocess.CalledProcessError as e:
        print(f"Failed to {command} the Tor service: {e}")


args = create_parser().parse_args()
log = set_loglevel(debug_mode=args.debug)
