#!/usr/bin/env sh

rm /usr/bin/geckodriver -v
apt remove tor --autoremove --purge -y
pip3 uninstall tor2tor -y -v
