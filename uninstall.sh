#!/bin/bash

# Remove the geckodriver binary from /usr/bin
rm /usr/bin/geckodriver -v

# Uninstall tor and its configuration files including unused packages (I might be doing you a favour by removing unused packages haha)
apt remove tor --autoremove --purge -y

# Uninstall tor2tor
pip3 uninstall tor2tor -y -v
echo "Cleanup complete."
