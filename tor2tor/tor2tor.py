import os
import re
from datetime import datetime

import requests
from PIL import Image
from rich import print
from rich.table import Table
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from .config import args, log, update_tor_path
from .coreutils import (
    clear_screen,
    construct_output_name,
    get_file_info,
    path_finder,
    HOME_DIRECTORY,
    start_tor,
    stop_tor,
)


def create_table(table_headers: list) -> Table:
    """
    Creates a rich table with the given column headers.

    :param table_headers: The column headers to add to the Table.
    :returns: A table with added column headers.
    """
    table = Table(show_header=True, header_style="bold white")
    for header in table_headers:
        table.add_column(header, style="dim" if header == "#" else "")
    return table


def add_http_to_link(link: str) -> str:
    """
    Adds 'http://' to the URL if it doesn't already start with 'http://' or 'https://'.

    :param link: The link to modify.
    :return: The modified URL.
    """
    if not link.startswith(("http://", "https://")):
        return f"http://{link}"
    return link


def capture_onion(onion_url: str, onion_index, driver: webdriver, table: Table):
    """
    Captures a screenshot of a given onion link using a webdriver.

    :param onion_url: The onion URL to capture.
    :param onion_index: The index of the onion link in a list or sequence.
    :param driver: The webdriver instance to use for capturing the screenshot.
    """

    # Construct the directory name based on the URL
    directory_name = construct_output_name(url=args.url)

    # Add HTTP to the URL if it's not already there
    validated_onion_link = add_http_to_link(link=onion_url)

    # Construct the filename for the screenshot from the onion link
    filename = construct_output_name(url=validated_onion_link) + ".png"

    # Construct the full file path
    file_path = os.path.join(HOME_DIRECTORY, "tor2tor", directory_name, filename)

    # Log the onion link being captured
    log.info(f"Capturing... {onion_index} {validated_onion_link}")

    # Navigate to the URL
    driver.get(validated_onion_link)

    # Take a screenshot
    driver.save_full_page_screenshot(file_path)

    # Log the successful capture
    log.info(f"[dim]{driver.title}[/] - [italic][link file://{filename}]{filename}[/]")

    # Add screenshot info to the Table
    dimensions, file_size, last_modified_time = get_file_info(filename=file_path)
    table.add_row(
        str(onion_index),
        f"[yellow]{filename}[/]",
        f"[purple]{dimensions}[/]",
        f"[cyan]{file_size}[/]",
        f"[blue]{last_modified_time}[/]",
    )

    # Open the image if the 'open' argument is True
    if args.open:
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
        log.warning(f"User Interruption detected ([yellow]Ctrl+C[/])")
    except Exception as e:
        log.error(f"[[red]X[/]] An error occurred: [red]{e}[/]")


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

        log.info(f"Found {len(valid_urls)} links on {onion_url}")

        return valid_urls

    except KeyboardInterrupt:
        log.warning(f"User Interruption detected ([yellow]Ctrl+C[/])")
    except Exception as e:
        log.error(f"An error occurred: [red]{e}[/]")


def start_tor2tor():
    """
    Starts the web scraping process to capture screenshots of onion websites.
    It categorizes the websites into online and offline based on their availability.

    Command-line arguments are parsed to set various options like headless mode, URL, etc.
    """

    # Lists to store online and offline onion URLs
    offline_onions = []
    online_onions = []

    # Record the start time for performance measurement
    start_time = datetime.now()

    # Check if a URL is provided for scraping
    if args.url:
        path_finder(url=args.url)

        clear_screen()
        start_tor()

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

        # Create a table where capture screenshots will be displayed
        screenshots_table = create_table(
            table_headers=[
                "#",
                "filename",
                "dimensions",
                "size (bytes)",
                "created",
            ]
        )

        # Loop through each onion URL and capture it
        for idx, onion in enumerate(onions, start=1):
            try:
                capture_onion(
                    onion_url=onion,
                    onion_index=idx,
                    driver=driver,
                    table=screenshots_table,
                )
                online_onions.append(onion)
                if idx == args.limit:
                    break
            except Exception as e:
                offline_onions.append(onion)
                log.warning(f"{idx} Skipped [yellow]{e}[/]")
                continue

        # Quit the webdriver and stop Tor
        driver.quit()
        stop_tor()

        # Print table showing captured onions
        print(screenshots_table)

        # Display the summary
        log.info(f"Captured: {len(online_onions)}")
        log.info(f"Skipped: {len(offline_onions)}")
        log.info(f"Finished in {datetime.now() - start_time} seconds.")

    # Handle the --tor argument for Windows systems
    elif args.tor:
        if os.name == "nt":
            update_tor_path(tor_path=args.tor)
        else:
            log.warning(
                f"t/--tor argument is not required on {os.name} systems, only the tor package is needed."
            )
