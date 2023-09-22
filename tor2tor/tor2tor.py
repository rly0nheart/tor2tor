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


def add_http_to_url(url: str):
    if not (url.startswith("http://") or url.startswith("https://")):
        return f"http://{url}"
    else:
        return url


def capture_onion(
    onion_link: str,
    onion_index,
    driver: webdriver,
    arguments: argparse,
):
    directory_name = construct_output_name(url=arguments.url)
    url = add_http_to_url(url=onion_link)
    filename = construct_output_name(url=url) + ".png"
    file_path = os.path.join(HOME_DIRECTORY, "tor2tor", directory_name, filename)

    print(f"[[blue]~[/]] {onion_index} Capturing: {url}")
    driver.get(url)

    # Take a screenshot
    driver.save_full_page_screenshot(file_path)
    print(
        f"[[green]+[/]] {onion_index} Captured: [dim]{driver.title}[/] - [italic][link file://{filename}]{filename}[/]"
    )
    if arguments.open:
        url_image = Image.open(file_path, "r")
        url_image.show()


def get_onion_response(url: str):
    proxies = {"http": "socks5h://localhost:9050", "https": "socks5h://localhost:9050"}
    # Replace this with your actual implementation
    response = requests.get(url, proxies=proxies)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup


def is_valid_onion(url):
    pattern = r"^(http(s)?://)?[a-z0-9]+\.onion(/[^\s]*)?$"
    return bool(re.match(pattern, url))


def get_onions_on_page(onion_url):
    valid_urls = []
    page_content = get_onion_response(onion_url)
    url_pattern = re.compile(
        r"https?://\S+"
    )  # Regular expression to match URLs that start with http/https.
    found_onions = page_content.find_all("a")  # Find all <a> tags in the html.
    for onion_index, onion in enumerate(found_onions, start=1):
        href = onion.get("href")
        if href:
            urls = url_pattern.findall(href)
            for url in urls:
                valid_urls.append(url)

    return valid_urls


def start_tor2tor():
    offline_onions = []
    online_onions = []

    args = create_parser().parse_args()
    start_time = datetime.now()

    if args.url:
        path_finder(url=args.url)
        start_tor()
        onions = get_onions_on_page(onion_url=add_http_to_url(url=args.url))
        clear_screen()
        print(f"[[blue]+[/]] Found {len(onions)} links on {args.url}")
        options = Options()
        if args.headless:
            options.add_argument("--headless")
        options.set_preference("network.proxy.type", 1)
        options.set_preference("network.proxy.socks", "127.0.0.1")
        options.set_preference("network.proxy.socks_port", 9050)
        options.set_preference("network.proxy.socks_version", 5)
        options.set_preference("network.proxy.socks_remote_dns", True)
        options.set_preference("network.dns.blockDotOnion", False)
        driver = webdriver.Firefox(options=options)

        for idx, onion in enumerate(onions, start=1):
            try:
                capture_onion(
                    onion_link=onion,
                    onion_index=idx,
                    driver=driver,
                    arguments=args,
                )
                online_onions.append(onion)
                if idx == args.limit:
                    break
            except Exception as e:
                offline_onions.append(onion)
                print(f"[[red]-[/]] {idx} Unavailable: {onion} - [red]{e}[/]")
                continue

        driver.quit()
        stop_tor()

        print(f"{'-'*50}")
        print(f"[[green]+[/]] Online onions: {len(online_onions)}")
        print(f"[[yellow]-[/]] Offline onions: {len(offline_onions)}")
        print(f"[[green]*[/]] Finished in {datetime.now() - start_time} seconds.")
    elif args.tor:
        if os.name == "nt":
            update_tor_path(tor_path=args.tor)
        else:
            print(
                f"t/--tor argument is not required on {os.name} systems, only the tor package is needed."
            )
