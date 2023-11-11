__author__ = "Richard Mwewa"
__about__ = "https://about.me/rly0nheart"
__version__ = "0.13.0"
__description__ = """
# Tor2Tor
> **Tor2Tor** scrapes a given onion link and captures screenshots of all links available on it.
"""

__epilog__ = f"""
# by [{__author__}]({__about__})
## Examples
### Local Installation
```
tor2tor http://example.onion
```

### Docker Container
```
docker run --tty --volume $PWD/tor2tor:/root/tor2tor rly0nheart/tor2tor http://example.onion
```"""
