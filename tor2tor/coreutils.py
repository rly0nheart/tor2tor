import os
import subprocess
from datetime import datetime
from urllib.parse import urlparse

from PIL import Image

from .config import load_data, log

# Construct path to the user's home directory
HOME_DIRECTORY = os.path.expanduser("~")


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
    :return: A formatted time string in the format hh:mm:ssAM/PM".
    """
    utc_from_timestamp = datetime.utcfromtimestamp(timestamp)
    time_object = utc_from_timestamp.strftime("%I:%M:%S %p")
    return time_object


def get_file_info(filename: str) -> tuple:
    """
    Gets a given file's information.

    :param filename: File to get info for.
    :return: A tuple containing the file's dimensions, size and last modified time.
    """
    with Image.open(filename) as image:
        dimensions = image.size

    file_size = os.path.getsize(filename=filename)

    last_modified_time = convert_timestamp(
        timestamp=os.path.getmtime(filename=filename)
    )

    return dimensions, file_size, last_modified_time


def clear_screen():  # -> a cleared screen
    """
    Clear the terminal screen/
    If Operating system is Windows, uses the 'cls' command. Otherwise, uses the 'clear' command

    :return: Uhh, a cleared screen? haha
    """
    subprocess.call("cmd.exe /c cls" if os.name == "nt" else "clear")


# Start the tor service
def start_tor():
    """
    Starts the Tor service based on the operating system.
    """
    tor_path = load_data().get("tor-path")
    try:
        if os.name == "nt":
            log.info(f"Configured tor.exe path: [link file://{tor_path}]{tor_path}")
            subprocess.Popen(tor_path)
        else:
            subprocess.run(["service", "tor", "start"])
    except Exception as e:
        log.error(f"Failed to start [link file://{tor_path}]{tor_path}: {e}")


def stop_tor():
    """
    Stops the Tor service based on the operating system.
    """
    try:
        if os.name == "nt":
            subprocess.Popen("taskkill /IM tor.exe /F")
        else:
            subprocess.run(["service", "tor", "stop"])
    except Exception as e:
        log.error(f"Failed to stop tor.exe: {e}")
