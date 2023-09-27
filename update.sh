#!/bin/bash

# Check if the directory has a .git folder
if [ -d ".git" ]; then
  # Fetch the latest updates from the https://github.com/rly0nheart/tor2tor
  git fetch origin

  # Compare local and remote branches
  LOCAL=$(git rev-parse @)
  REMOTE=$(git rev-parse @{u})

  # Check if the local repository is up-to-date
  if [ $LOCAL = $REMOTE ]; then
    echo "Tor2Tor is up-to-date."
  else
    echo "Pulling the latest changes. Please wait..."
    git pull

    # Install tor2tor after pulling the updates
    pip3 install .
  fi
else
  echo "Current directory is not a Git repository."
fi
