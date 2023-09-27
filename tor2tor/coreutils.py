import os
import time
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
HOME_DIRECTORY = os.path.expanduser("~")


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


def usage():
    return """
    tor2tor http://example.onion
    
    docker run --tty --volume rly0nheart/tor2tor http://example.onion
    """


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
            RichHandler(markup=True, log_time_format="%I:%M:%S%p", show_level=False)
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
    directories = ["tor2tor", os.path.join("tor2tor", construct_output_name(url=url))]
    for directory in directories:
        # Construct and create each directory from the directories list if it doesn't already exist
        os.makedirs(os.path.join(HOME_DIRECTORY, directory), exist_ok=True)


def convert_timestamp(timestamp: float) -> str:
    """
    Converts a Unix timestamp to a formatted datetime string.

    :param timestamp: The Unix timestamp to be converted.
    :return: A formatted time string in the format "hh:mm:ssAM/PM".
    """
    utc_from_timestamp = datetime.utcfromtimestamp(timestamp)
    time_object = utc_from_timestamp.strftime("%I:%M:%S %p")
    return time_object


def get_file_info(filename: str) -> tuple:
    """
    Gets a given file's information.

    :param filename: File to get info for.
    :return: A tuple containing the file's size and created time.
    """
    file_size = os.path.getsize(filename=filename)

    created_time = convert_timestamp(timestamp=os.path.getmtime(filename=filename))

    return file_size, created_time


def tor_service(command: str):
    """
    Starts/Stops the Tor service based on the provided command.

    :param command: A command that determines whether the tor service should be started or stopped ("start", "stop").
    """
    subprocess.run(["service", "tor", command])


args = create_parser().parse_args()
log = set_loglevel(debug_mode=args.debug)
