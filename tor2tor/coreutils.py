import os
import subprocess
import time
from urllib.parse import urlparse

from .config import settings

# Construct path to the user's home directory
HOME_DIRECTORY = os.path.expanduser("~")


def construct_output_name(url: str):
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


def clear_screen() -> None:
    """
    Clear the terminal screen/
    If Operating system is Windows, uses the 'cls' command. Otherwise, uses the 'clear' command

    :return: Uhh a cleared screen? haha
    """
    subprocess.call("cmd.exe /c cls" if os.name == "nt" else "clear")


# Start the tor service
def start_tor():
    tor_path = settings().get("tor-path")
    if os.name == "nt":
        print(f"Configured Tor binary path: {tor_path}")
        subprocess.Popen(tor_path)
    else:
        subprocess.run(["sudo", "service", "tor", "start"])
        print(f"Started tor service: {time.asctime()}")


# Stop the tor service
def stop_tor():
    if os.name == "nt":
        subprocess.Popen("taskkill /IM tor.exe /F")
    else:
        subprocess.run(["sudo", "service", "tor", "stop"])
        print(f"Stopped tor service: {time.asctime()}")
