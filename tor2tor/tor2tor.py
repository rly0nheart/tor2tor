import os
import re
import argparse
from datetime import datetime

import requests
from PIL import Image
from rich import print
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from .config import create_parser, update_tor_path
from .coreutils import (
    clear_screen,
    construct_output_name,
    path_finder,
    HOME_DIRECTORY,
    start_tor,
    stop_tor,
)


def add_http_to_link(link: str) -> str:
    """
    Adds 'http://' to the URL if it doesn't already start with 'http://' or 'https://'.

    :param link: The link to modify.
    :return: The modified URL.
    """
    if not link.startswith(("http://", "https://")):
        return f"http://{link}"
    return link


def capture_onion(
    onion_url: str,
    onion_index,
    driver: webdriver,
    arguments: argparse,
):
    """
    Captures a screenshot of a given onion link using a webdriver.

    :param onion_url: The onion URL to capture.
    :param onion_index: The index of the onion link in a list or sequence.
    :param driver: The webdriver instance to use for capturing the screenshot.
    :param arguments: Command-line arguments parsed using argparse.
    """

    # Construct the directory name based on the URL
    directory_name = construct_output_name(url=arguments.url)

    # Add HTTP to the URL if it's not already there
    validated_onion_link = add_http_to_link(link=onion_url)

    # Construct the filename for the screenshot from the onion link
    filename = construct_output_name(url=validated_onion_link) + ".png"

    # Construct the full file path
    file_path = os.path.join(HOME_DIRECTORY, "tor2tor", directory_name, filename)

    # Log the onion link being captured
    print(f"[[blue]*[/]] {onion_index} Capturing: {validated_onion_link}")

    # Navigate to the URL
    driver.get(validated_onion_link)

    # Take a screenshot
    driver.save_full_page_screenshot(file_path)

    # Log the successful capture
    print(
        f"[[green]+[/]] {onion_index} [dim]{driver.title}[/]: [italic][link file://{filename}]{filename}[/]"
    )

    # Open the image if the 'open' argument is True
    if arguments.open:
        url_image = Image.open(file_path, "r")
        url_image.show()


def get_onion_response(onion_url: str) -> BeautifulSoup:
    """
    Fetches the HTML content of a given onion link using a SOCKS5 proxy.

    :param onion_url: The onion URL to fetch the content from.
    :return: A BeautifulSoup object containing the parsed HTML content.
    """

    try:
        # Define the SOCKS5 proxy settings
        proxies = {
            "http": "socks5h://localhost:9050",
            "https": "socks5h://localhost:9050",
        }

        # Perform the HTTP GET request
        response = requests.get(onion_url, proxies=proxies)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        return soup
    except KeyboardInterrupt:
        print(f"[[yellow]-[/]] User Interruption detected ([yellow]Ctrl+C[/])")
    except Exception as e:
        print(f"[[red]X[/]] An error occurred: [red]{e}[/]")


def is_well_formed_onion(onion_link: str) -> bool:
    """
    Checks if the given URL is a well-formed onion link.

    :param onion_link: The onion link to validate.
    :return: True if the URL is a well-formed onion link, False otherwise.

    Regex Explanation:
    -----------------
    - `^(http(s)?://)?`: Matches the start of the string, and optionally matches 'http://' or 'https://'.
    - `[a-z0-9]+`: Matches one or more alphanumeric characters, which form the subdomain of the onion link.
    - `\.onion`: Matches the '.onion' TLD (Top-Level Domain).
    - `(/[^\s]*)?$`: Optionally matches a forward slash followed by zero or more non-whitespace characters,
       and then the end of the string.
    """

    # Define the regex pattern for a well-formed onion URL
    pattern = r"^(http(s)?://)?[a-z0-9]+\.onion(/[^\s]*)?$"

    # Use regex to validate the URL
    return bool(re.match(pattern, onion_link))


def get_onions_on_page(onion_url: str) -> list:
    """
    Scrapes a given onion URL and extracts all valid URLs found in <a> tags.

    :param onion_url: The onion URL to scrape.
    :return: A list of valid URLs found on the page.

    Regex Explanation:
    -----------------
    - `https?`: Matches either 'http' or 'https'.
    - `://`: Matches the '://' that follows the protocol.
    - `\S+`: Matches one or more non-whitespace characters.
    """

    print(f"[[green]~[/]] Scraping: {onion_url}")

    # Initialize an empty list to store valid URLs
    valid_urls = []

    try:
        # Fetch the page content
        page_content = get_onion_response(onion_url=onion_url)

        # Define the regex pattern to match URLs
        url_pattern = re.compile(r"https?://\S+")

        # Find all <a> tags in the HTML content
        found_onions = page_content.find_all("a")

        # Loop through each <a> tag and extract the href attribute
        for onion_index, onion in enumerate(found_onions, start=1):
            href = onion.get("href")
            if href:
                urls = url_pattern.findall(href)
                for url in urls:
                    valid_urls.append(url)

        print(f"[[blue]+[/]] Found {len(valid_urls)} links.")

        return valid_urls

    except KeyboardInterrupt:
        print(f"[[yellow]-[/]] User Interruption detected ([yellow]Ctrl+C[/])")
    except Exception as e:
        print(f"[[red]X[/]] An error occurred: [red]{e}[/]")


def start_tor2tor():
    """
    Starts the web scraping process to capture screenshots of onion websites.
    It categorizes the websites into online and offline based on their availability.

    Command-line arguments are parsed to set various options like headless mode, URL, etc.
    """

    # Lists to store online and offline onion URLs
    offline_onions = []
    online_onions = []

    # Parse command-line arguments
    args = create_parser().parse_args()

    # Record the start time for performance measurement
    start_time = datetime.now()

    # Check if a URL is provided for scraping
    if args.url:
        path_finder(url=args.url)
        start_tor()

        clear_screen()

        # Fetch onion URLs from the provided URL
        onions = get_onions_on_page(onion_url=add_http_to_link(link=args.url))

        # Configure Firefox webdriver options
        options = Options()
        if args.headless:
            options.add_argument("--headless")
        options.set_preference("network.proxy.type", 1)
        options.set_preference("network.proxy.socks", "127.0.0.1")
        options.set_preference("network.proxy.socks_port", 9050)
        options.set_preference("network.proxy.socks_version", 5)
        options.set_preference("network.proxy.socks_remote_dns", True)
        options.set_preference("network.dns.blockDotOnion", False)

        # Initialize the webdriver
        driver = webdriver.Firefox(options=options)

        # Loop through each onion URL to capture it
        for idx, onion in enumerate(onions, start=1):
            try:
                capture_onion(
                    onion_url=onion,
                    onion_index=idx,
                    driver=driver,
                    arguments=args,
                )
                online_onions.append(onion)
                if idx == args.limit:
                    break
            except Exception as e:
                offline_onions.append(onion)
                print(f"[[yellow]*[/]] {idx} Unavailable/Skipping: [yellow]{e}[/]")
                continue

        # Quit the webdriver and stop Tor
        driver.quit()
        stop_tor()

        # Display the summary
        print(f"{'-'*50}")
        print(f"[[green]+[/]] Available onions: {len(online_onions)}")
        print(f"[[yellow]-[/]] Unavailable/Skipped onions: {len(offline_onions)}")
        print(f"[[green]*[/]] Finished in {datetime.now() - start_time} seconds.")

    # Handle the --tor argument for Windows systems
    elif args.tor:
        if os.name == "nt":
            update_tor_path(tor_path=args.tor)
        else:
            print(
                f"t/--tor argument is not required on {os.name} systems, only the tor package is needed."
            )
