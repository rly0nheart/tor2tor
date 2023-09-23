import os
import time
import subprocess
from datetime import datetime
from urllib.parse import urlparse

from PIL import Image
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

def format_time_difference(current_time: float, past_time: float) -> string:
    """
    Format the time difference between the current time and a past time.
    
    :param current_time: (float) The current time as a Unix timestamp.
    :param past_time: (float) The past time as a Unix timestamp.
    :return: A string representing the time difference in a human-readable format.
    """
    
    # Calculate the time difference in seconds
    time_difference = int(current_time - past_time)
    
    # If the time difference is less than 1 second, return "now"
    if time_difference < 1:
        return "now"
    
    # If the time difference is less than 60 seconds, return in seconds
    if time_difference < 60:
        return f"{time_difference} seconds ago"
    
    # Convert time difference to minutes and check if less than 60 minutes
    minutes = time_difference // 60
    if minutes < 60:
        return f"{minutes} minutes ago"
    
    # Convert time difference to hours and check if less than 24 hours
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hours ago"

    # For times older than a day, return the exact date and time
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(past_time))
    
    
def get_file_info(filename: str) -> tuple:
  """
  Gets a given file's information.
  
  :param filename: File to get info for.
  :return: A tuple containing the file's dimensions, size and last modified time.
  """
  dimensions = None
  with Image.open(filename) as image:
      dimensions = image.size
      
  file_size = os.path.getsize(filename)
  last_modified_time = format_time_difference(current_time=time.time(), past_time=os.path.getmtime(filename))
  
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
