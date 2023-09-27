#!/bin/bash

# Install the Tor package without installing recommended packages.
apt-get update && apt-get install -y --no-install-recommends tor

# Download geckodriver .tar.gz file and pipe it to 'tar' to extract the geckodriver binary directly into /usr/bin.
curl -L https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz | \
    tar xz -C /usr/bin

# Install Python packages defined in the current directory's setup.py/pyproject.toml file. (pyproject.toml in this case)
pip3 install .
