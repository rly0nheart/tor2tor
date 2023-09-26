#!/bin/env sh

apt-get update && apt-get install -y --no-install-recommends tor

curl -L https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz | \
    tar xz -C /usr/bin

pip3 install .
