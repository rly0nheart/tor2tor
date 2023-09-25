import os
import re
import time
from datetime import datetime
from queue import Queue
from threading import Lock, Thread

import requests
from rich import print
from rich.table import Table
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from .coreutils import args, log, __version__, check_updates
from .coreutils import (
    show_banner,
    clear_screen,
    tor_service,
    add_http_to_link,
    construct_output_name,
    get_file_info,
    path_finder,
    create_table,
    HOME_DIRECTORY,
)


# Create lock for logging and table updates
log_lock = Lock()
table_lock = Lock()


def firefox_options() -> Options:
    """
    Configure Firefox options for web scraping with a headless browser and Tor network settings.

    :returns: A Selenium WebDriver Options object with preset configurations.
    """
    options = Options()
    if args.headless:
        options.add_argument("--headless")
    options.set_preference("network.proxy.type", 1)
    options.set_preference("network.proxy.socks", "127.0.0.1")
    options.set_preference("network.proxy.socks_port", 9050)
    options.set_preference("network.proxy.socks_version", 5)
    options.set_preference("network.proxy.socks_remote_dns", True)
    options.set_preference("network.dns.blockDotOnion", False)
    return options


def open_firefox_pool(pool_size: int) -> Queue:
    """
    Initializes a queue of Firefox WebDriver instances for future use.

    :param pool_size: The number of Firefox instances to create.
    :return: A queue containing the created Firefox instances.
    """
    # Initialize a new queue to hold the Firefox instances.
    pool = Queue()

    log.info(f"Opening WebDriver pool with {args.pool_size} instances...")

    # Populate the pool with Firefox instances.
    for _ in range(pool_size):  # Create 3 (default) instances
        driver = webdriver.Firefox(options=firefox_options())
        pool.put(driver)

    return pool


def close_firefox_pool(pool: Queue):
    """
    Closes all the Firefox instances in the pool.

    :param pool: The pool containing Firefox WebDriver instances to close.
    """
    log.info(f"Closing WebDriver pool...")
    while not pool.empty():
        driver = pool.get()
        driver.quit()


def worker(queue: Queue, screenshots_table: Table, pool: Queue):
    """
    Worker function to capture screenshots of websites.

    This function is intended to be used as a target for a Thread. It captures screenshots
    of websites as tasks are fed via the queue. The function borrows a Firefox instance from
    the pool for each task and returns it after the task is complete.

    :param queue: The queue containing tasks (websites to capture).
    :param screenshots_table: A table where captured screenshot metadata is stored.
    :param pool: The pool of Firefox WebDriver instances.
    """
    # Continue working as long as the queue is not empty
    while not queue.empty():
        # Get a new task from the queue
        idx, onion = queue.get()

        # Borrow a Firefox instance from the pool
        driver = pool.get()

        # Capture the screenshot
        capture_onion(onion, idx, driver, screenshots_table)

        # Return the Firefox instance back to the pool
        pool.put(driver)

        # Mark the task as done
        queue.task_done()


def capture_onion(onion_url: str, onion_index, driver: webdriver, table: Table):
    """
    Captures a screenshot of a given onion link using a webdriver.

    :param onion_url: The onion URL to capture.
    :param onion_index: The index of the onion link in a list or sequence.
    :param driver: The webdriver instance to use for capturing the screenshot.
    :param table: Table to add captured screenshots to.
    """

    # Construct the directory name based on the URL
    directory_name = construct_output_name(url=args.onion)

    # Add HTTP to the URL if it's not already there
    validated_onion_link = add_http_to_link(link=onion_url)

    # Construct the filename for the screenshot from the onion link
    filename = construct_output_name(url=validated_onion_link) + ".png"

    # Construct the full file path
    file_path = os.path.join(HOME_DIRECTORY, "tor2tor", directory_name, filename)

    # Log the onion link being captured
    log.info(f"{onion_index} Capturing... {validated_onion_link}")

    # Navigate to the URL
    driver.get(validated_onion_link)

    if os.path.exists(path=file_path):
        log.info(f"[yellow][italic]{filename}[/][/] already exists.")
    else:
        # Take a screenshot
        driver.save_full_page_screenshot(file_path)

        with log_lock:
            # Log the successful capture
            log.info(
                f"[dim]{driver.title}[/] - [yellow][italic][link file://{filename}]{filename}[/][/]"
            )

        with table_lock:
            # Add screenshot info to the Table
            file_size, created_time = get_file_info(filename=file_path)
            table.add_row(
                str(onion_index),
                f"[yellow][italic]{filename}[/][/]",
                f"[cyan]{file_size}[/]",
                f"[blue]{created_time}[/]",
            )


def get_onion_response(onion_url: str) -> BeautifulSoup:
    """
    Fetches the HTML content of a given onion link using a SOCKS5 proxy.

    :param onion_url: The onion URL to fetch the content from.
    :return: A BeautifulSoup object containing the parsed HTML content.
    """

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


def start():
    """
    Main entrypoint to start the web scraping process and capture screenshots of onion websites.
    """
    firefox_pool = None  # Initialize to None so it's accessible in the finally block
    start_time = datetime.now()  # Record the start time for performance measurement
    try:
        tor_service(command="start")  # Start the Tor service.

        clear_screen()
        path_finder(
            url=args.onion
        )  # Create a directory with the onion link as the name.
        show_banner()
        log.info(f"Starting 🧅Tor2Tor {__version__} {time.asctime()}...")
        check_updates()

        # Fetch onion URLs from the provided URL
        onions = get_onions_on_page(onion_url=add_http_to_link(link=args.onion))

        firefox_pool = open_firefox_pool(pool_size=args.pool_size)

        # Create a table where capture screenshots will be displayed
        screenshots_table = create_table(
            table_headers=["#", "filename", "size (bytes)", "created"]
        )

        # Initialize Queue and add tasks
        queue = Queue()
        for idx, onion in enumerate(onions, start=1):
            try:
                queue.put((idx, onion))
                if (
                    idx == args.limit
                ):  # If onion index is equal to the limit set in -l/--limit, break the loop.
                    break
            except KeyboardInterrupt:
                log.warning(f"User Interruption detected ([yellow]Ctrl+C[/])")
                exit()
            except Exception as e:
                log.warning(f"{idx} Skipped [yellow]{e}[/]")
                continue

        # Initialize threads
        threads = []
        for _ in range(args.workers):  # create 3 (default) worker threads
            t = Thread(target=worker, args=(queue, screenshots_table, firefox_pool))
            t.start()
            threads.append(t)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        # Print table showing captured onions
        print(screenshots_table)
        print("\n")

    except KeyboardInterrupt:
        log.warning(f"User Interruption detected ([yellow]Ctrl+C[/])")
        exit()
    except Exception as e:
        log.error(f"An error occurred: [red]{e}[/]")
        exit()
    finally:
        tor_service(command="stop")
        if firefox_pool is not None:
            close_firefox_pool(pool=firefox_pool)
        log.info(f"Finished in {datetime.now() - start_time} seconds.")
