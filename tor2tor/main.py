from datetime import datetime

from .tor2tor import sys, log, args, Tor2Tor
from .coreutils import (
    __version__,
    path_finder,
    show_banner,
    check_updates,
    tor_service,
    is_valid_onion,
)


def execute_tor2tor():
    target_onion = args.onion
    pool_size = args.pool
    start_time = datetime.now()  # Record the start time for performance measurement
    tor2tor = Tor2Tor()

    firefox_pool = None

    if is_valid_onion(url=target_onion):
        try:
            path_finder(
                url=target_onion
            )  # Create a directory with the onion link as the name.

            show_banner()
            check_updates()

            log.info(f"Starting 🧅Tor2Tor {__version__} {start_time}...")
            tor_service(command="start")  # Start the Tor service.
            firefox_pool = tor2tor.open_firefox_pool(pool_size=pool_size)
            tor2tor.execute_scraper(
                target_onion=target_onion,
                firefox_pool=firefox_pool,
                worker_threads=args.threads,
            )
        except KeyboardInterrupt:
            log.warning(f"User Interruption detected ([yellow]Ctrl+C[/])")
            sys.exit()
        except Exception as e:
            log.error(f"An error occurred: [red]{e}[/]")
            sys.exit()
        finally:
            if firefox_pool is not None:
                tor2tor.close_firefox_pool(pool=firefox_pool)

            tor_service(command="stop")  # Stop the Tor service.
            log.info(f"Stopped in {datetime.now() - start_time} seconds.")
    else:
        log.warning(f"{target_onion} does not seem to be a valid onion.")
