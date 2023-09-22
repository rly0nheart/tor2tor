import os
import subprocess
from urllib.parse import urlparse

from rich import print
from .config import load_data

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
            print(f"[[green]*[/]] Configured Tor binary path: {tor_path}")
            subprocess.Popen(tor_path)
        else:
            subprocess.run(["service", "tor", "start"])
    except Exception as e:
        print(f"Failed to start Tor: {e}")


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
        print(f"Failed to stop Tor: {e}")
