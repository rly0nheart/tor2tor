import os
import re
import sys
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

from . import __version__
from .coreutils import (
    log,
    args,
    tor_service,
    create_table,
    load_settings,
    check_updates,
    get_file_info,
    is_valid_onion,
    PROGRAM_DIRECTORY,
    add_http_to_link,
    construct_output_name,
    convert_timestamp_to_datetime
)


class Tor2Tor:
    def __init__(self):
        # Initialise locks for logging and table updates
        self.log_lock = Lock()
        self.table_lock = Lock()

        # Initialise queues for storing captured and skipped onions
        self.captured_onions_queue = Queue()
        self.skipped_onions_queue = Queue()

        # Initialise tor proxy settings
        self.socks_host = load_settings().get("proxy").get("socks5").get("host")
        self.socks_port = load_settings().get("proxy").get("socks5").get("port")
        self.socks_type = load_settings().get("proxy").get("socks5").get("type")
        self.socks_version = load_settings().get("proxy").get("socks5").get("version")

    def firefox_options(self, instance_index: int) -> Options:
        """
        Configure Firefox options for web scraping with a headless browser and Tor network settings.

        :param instance_index: Index of the opened WebDriver instance in the firefox_pool.
        :returns: A Selenium WebDriver Options object with preset configurations.
        """
        options = Options()
        if args.headless:
            options.add_argument("--headless")
            log.info(f"Running headless on WebDriver instance {instance_index}...")
        options.set_preference("network.proxy.type", self.socks_type)
        options.set_preference("network.proxy.socks", self.socks_host)  # "127.0.0.1"
        options.set_preference("network.proxy.socks_port", self.socks_port)
        options.set_preference("network.proxy.socks_version", self.socks_version)
        options.set_preference("network.proxy.socks_remote_dns", True)
        options.set_preference("network.dns.blockDotOnion", False)
        return options

    def open_firefox_pool(self, pool_size: int) -> Queue:
        """
        Initializes a queue of Firefox WebDriver instances for future use.

        :param pool_size: The number of Firefox instances to create.
        :return: A queue containing the created Firefox instances.
        """
        # Initialize a new queue to hold the Firefox instances.
        pool = Queue()

        log.info(f"Opening WebDriver pool with {pool_size} instances...")

        # Populate the pool with Firefox instances.
        for instance_index, webdriver_instance in enumerate(
            range(pool_size), start=1
        ):  # Create 3 (default) instances
            driver = webdriver.Firefox(
                options=self.firefox_options(instance_index=instance_index),
            )
            pool.put(driver)

        return pool

    @staticmethod
    def close_firefox_pool(pool: Queue):
        """
        Closes all the Firefox instances in the pool.

        :param pool: The pool containing Firefox WebDriver instances to close.
        """
        log.info("Closing WebDriver pool...")
        while not pool.empty():
            driver = pool.get()
            driver.quit()

    def worker(self, tasks_queue: Queue, screenshots_table: Table, firefox_pool: Queue):
        """
        Worker function to capture screenshots of websites.

        This function is intended to be used as a target for a Thread. It captures screenshots
        of websites as tasks are fed via the queue. The function borrows a Firefox instance from
        the pool for each task and returns it after the task is complete.

        :param tasks_queue: The queue containing tasks (websites to capture).
        :param screenshots_table: A table where captured screenshot metadata is stored.
        :param firefox_pool: The pool of Firefox WebDriver instances.
        """
        onion_index = None
        driver = None
        onion = None

        # Continue working as long as the queue is not empty
        while not tasks_queue.empty():
            try:
                # Get a new task from the queue
                onion_index, onion = tasks_queue.get()

                # If the task onion is valid, borrow a Firefox instance from the pool
                # And try to capture it.S
                if is_valid_onion(url=onion):
                    driver = firefox_pool.get()

                    # Capture the screenshot
                    self.capture_onion(
                        onion_url=onion,
                        onion_index=onion_index,
                        driver=driver,
                        screenshots_table=screenshots_table,
                    )
                    self.captured_onions_queue.put(
                        (
                            onion_index,
                            onion,
                            convert_timestamp_to_datetime(timestamp=time.time()),
                        )
                    )

                    # On successful capture, return the Firefox instance back to the pool and mark the task as done
                    # Do the same on exception.
                    firefox_pool.put(driver)
                    tasks_queue.task_done()
                else:
                    log.warning(
                        f"{onion_index} {onion} does not seem to be a valid onion. Skipping..."
                    )
                    # Add the invalid onion to the skipped_onions queue
                    self.skipped_onions_queue.put(
                        (
                            onion_index,
                            onion,
                            "[yellow]Invalid onion[/]",
                            convert_timestamp_to_datetime(timestamp=time.time()),
                        )
                    )

            except KeyboardInterrupt:
                log.warning("User interruption detected ([yellow]Ctrl+C[/])")
                sys.exit()
            except Exception as e:
                if args.log_skipped:
                    log.error(f"{onion_index} Skipping... [yellow]{e}[/]")

                # Add the skipped onion index, the onion itself, the time it was skipped, and the reason it was skipped
                self.skipped_onions_queue.put(
                    (
                        onion_index,
                        onion,
                        f"[red]{e}[/]",
                        convert_timestamp_to_datetime(timestamp=time.time()),
                    )
                )

                firefox_pool.put(driver)
                tasks_queue.task_done()

    def execute_worker(
        self,
        worker_threads: int,
        tasks_queue: Queue,
        screenshots_table: Table,
        firefox_pool: Queue,
    ):
        """
        Executes the worker method.

        :param worker_threads: Number of threads to execute the worker with.
        :param tasks_queue: The queue containing tasks (websites to capture).
        :param screenshots_table: The table where captured screenshots will be added.
        :param firefox_pool: A pool containing n number of firefox instances.
        """
        # Initialize threads
        threads = []
        for _ in range(worker_threads):  # create 3 (default) worker threads
            t = Thread(
                target=self.worker, args=(tasks_queue, screenshots_table, firefox_pool)
            )
            t.start()
            threads.append(t)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

    def get_onion_response(self, onion_url: str) -> BeautifulSoup:
        """
        Fetches the HTML content of a given onion link using a SOCKS5 proxy.

        :param onion_url: The onion URL to fetch the content from.
        :return: A BeautifulSoup object containing the parsed HTML content.
        """

        # Define the SOCKS5 proxy settings
        proxies = {
            "http": f"socks5h://{self.socks_host}:{self.socks_port}",
            "https": f"socks5h://{self.socks_host}:{self.socks_port}",
        }

        # Perform the HTTP GET request
        response = requests.get(onion_url, proxies=proxies)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        return soup

    def get_onions_on_page(self, onion_url: str) -> list:
        """
        Scrapes a given onion URL and extracts all valid URLs found in <a> tags.

        :param onion_url: The onion URL to scrape.
        :return: A list of valid URLs found on the page.

        Regex Explanation:
        -----------------
        - `https?`: Matches either 'http' or 'https'.
        - `://`: Matches the '://' that follows the protocol.
        - `\\S+`: Matches one or more non-whitespace characters.
        """

        # Initialize an empty list to store valid URLs
        valid_onions = []

        # Fetch the page content
        page_content = self.get_onion_response(onion_url=onion_url)

        # Define the regex pattern to match URLs
        url_pattern = re.compile(r"https?://\S+")

        # Find all <a> tags in the HTML content
        found_onions = page_content.find_all("a")

        # Loop through each <a> tag and extract the href attribute
        for onion_index, onion in enumerate(found_onions, start=1):
            href = onion.get("href")
            # Check if the 'href' attribute exists and is not None
            if href:
                # Find all URLs in the 'href' attribute using the regex pattern
                urls = url_pattern.findall(href)
                # Loop through each URL found in the 'href' attribute
                for url in urls:
                    # Check if the URL is a valid Onion URL
                    if is_valid_onion(url):
                        # Append the valid Onion URL to the list of valid_onion_urls
                        valid_onions.append(url)

        log.info(f"Found {len(valid_onions)} links on {onion_url}")
        return valid_onions

    def capture_onion(
        self, onion_url: str, onion_index, driver: webdriver, screenshots_table: Table
    ):
        """
        Captures a screenshot of a given onion link using a webdriver.

        :param onion_url: The onion URL to capture.
        :param onion_index: The index of the onion link in a list or sequence.
        :param driver: The webdriver instance to use for capturing the screenshot.
        :param screenshots_table: Table to add captured screenshots to.
        """

        # Construct the directory name based on the URL
        directory_name = construct_output_name(url=args.onion)

        # Add HTTP to the URL if it's not already there
        validated_onion_link = add_http_to_link(link=onion_url)

        # Construct the filename for the screenshot from the onion link
        filename = construct_output_name(url=validated_onion_link) + ".png"

        # Construct the full file path
        file_path = os.path.join(PROGRAM_DIRECTORY, directory_name, filename)

        # Log the onion link being captured
        log.info(f"{onion_index} Capturing... {validated_onion_link}")

        # Navigate to the URL
        driver.get(validated_onion_link)

        if os.path.exists(path=file_path):
            log.info(f"{onion_index} [yellow][italic]{filename}[/][/] already exists.")
        else:
            # Take a full screenshot of the onion and save it to the given file path
            driver.save_full_page_screenshot(file_path)

            with self.log_lock:
                # Log the successful capture
                log.info(
                    f"{onion_index} [dim]{driver.title}[/] - [yellow][italic][link file://{filename}]{filename}[/][/]"
                )

            with self.table_lock:
                # Add screenshot info to the Table
                file_size, created_time = get_file_info(filename=file_path)
                screenshots_table.add_row(
                    str(onion_index),
                    filename,
                    str(file_size),
                    str(created_time),
                )

    def execute_scraper(
        self,
        target_onion: str,
        pool_size: int,
        worker_threads: int,
    ):
        """
        Executes the scraper code.

        :param target_onion: The onion to scrape.
        :param pool_size: Size of the WebDriver instance pool (default is 3).
        :param worker_threads: Number of threads.
        """
        firefox_pool = None

        start_time = datetime.now()
        log.info(f"Starting 🧅Tor2Tor {__version__} {start_time}...")

        try:
            check_updates()

            tor_service(command="start")  # Start the Tor service.

            # Fetch onion URLs from the provided URL
            onions = self.get_onions_on_page(
                onion_url=add_http_to_link(link=target_onion)
            )

            firefox_pool = self.open_firefox_pool(pool_size=pool_size)

            # Create a table where capture screenshots will be displayed
            screenshots_table = create_table(
                table_title="Screenshots",
                table_headers=["#", "filename", "size (bytes)", "timestamp"],
            )

            # Initialize Queue and add tasks
            tasks_queue = Queue()

            for onion_index, onion in enumerate(onions, start=1):
                tasks_queue.put((onion_index, onion))

                if onion_index == args.limit:
                    # If onion index is equal to the limit set in -l/--limit, break the loop.
                    break

            self.execute_worker(
                worker_threads=worker_threads,
                tasks_queue=tasks_queue,
                screenshots_table=screenshots_table,
                firefox_pool=firefox_pool,
            )

            log.info("DONE!\n")

            # Print table showing captured screenshots
            print(screenshots_table)
            print("\n")

            # Print the summary tables for captured and skipped onions
            captured_onions, skipped_onions = self.onion_summary_tables(
                captured_onions=list(self.captured_onions_queue.queue),
                skipped_onions=list(self.skipped_onions_queue.queue),
            )

            log.info(f"{len(self.captured_onions_queue.queue)} onions captured.")
            print(captured_onions)

            log.info(f"{len(self.skipped_onions_queue.queue)} onions skipped.")
            print(skipped_onions)

        except KeyboardInterrupt:
            log.warning(f"User Interruption detected ([yellow]Ctrl+C[/])")
            sys.exit()
        except Exception as e:
            log.error(f"An error occurred: [red]{e}[/]")
            sys.exit()
        finally:
            if firefox_pool is not None:
                self.close_firefox_pool(pool=firefox_pool)

            tor_service(command="stop")  # Stop the Tor service.
            log.info(f"Stopped in {datetime.now() - start_time} seconds.")

    @staticmethod
    def onion_summary_tables(
        captured_onions: list,
        skipped_onions: list,
    ) -> tuple:
        """
        Creates tables showing a summary of captured and skipped onions.

        Note
        ----
        - The index value in the loops, holds the index of the onion in the captured/skipped onions lists
        - And the *_onion[0] holds the index of the onion from the scraper task.

        :param captured_onions: A list of tuples, each containing the captured onion url and its index
         from the scraper task.
        :param skipped_onions: A list of tuples,
           each containing the skipped onion url and its index from the scraper task.
        :returns: A tuple containing the captured and skipped onions tables:
           (captured_onions_table, skipped_onions_table).
        """

        # Create a table of captured onions
        captured_onions_table = create_table(
            table_headers=["#", "index", "onion", "timestamp"],
        )
        for index, captured_onion in enumerate(captured_onions, start=1):
            captured_onions_table.add_row(
                str(index),  # Index of the onion from the captured_onions list
                str(captured_onion[0]),  # Index of the onion from the scraping task
                str(captured_onion[1]),  # Onion url
                str(captured_onion[2]),  # Time the onion was captured
            )

        # Create a table of skipped onions
        skipped_onions_table = create_table(
            table_headers=["#", "index", "onion", "reason", "timestamp"],
        )
        for index, skipped_onion in enumerate(skipped_onions, start=1):
            skipped_onions_table.add_row(
                str(index),  # Index of the onion from the skipped_onions list
                str(skipped_onion[0]),  # Index of the onion from the scraping task
                str(skipped_onion[1]),  # Onion url
                str(skipped_onion[2]),  # Reason the onion was skipped
                str(skipped_onion[3]),  # Time the onion was skipped
            )

        return captured_onions_table, skipped_onions_table
