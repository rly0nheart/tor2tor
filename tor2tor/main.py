from .tor2tor import log, args, Tor2Tor
from .coreutils import (
    path_finder,
    is_valid_onion,
)


def execute_tor2tor():
    target_onion = args.onion
    tor2tor = Tor2Tor()

    if is_valid_onion(url=target_onion):
        print("""
┏┳┓     ┏┳┓    
 ┃ ┏┓┏┓┓ ┃ ┏┓┏┓
 ┻ ┗┛┛ ┗ ┻ ┗┛┛ """
              )
        path_finder(
            url=target_onion
        )  # Create a directory with the onion link as the name.

        tor2tor.execute_scraper(
            target_onion=target_onion,
            pool_size=args.pool,
            worker_threads=args.threads,
        )

    else:
        log.warning(f"{target_onion} does not seem to be a valid onion.")
