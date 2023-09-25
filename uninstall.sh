#!/usr/bin/sh

rm /usr/local/bin/geckodriver -v
apt remove tor --autoremove --purge -y
pip3 uninstall tor2tor -y -v
