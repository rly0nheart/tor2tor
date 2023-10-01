# Check if the directory has a .git folder
if (Test-Path ".git") {

    # Fetch the latest updates
    git fetch origin

    # Compare local and remote branches
    $LOCAL = git rev-parse @
    $REMOTE = git rev-parse "@{u}"

    # Check if the local repository is up-to-date
    if ($LOCAL -eq $REMOTE) {
        Write-Host "Tor2Tor is up-to-date."
    } else {
        Write-Host "Pulling the latest changes. Please wait..."
        git pull

        # Install tor2tor after pulling the updates
        pip3 install .
        Write-Host "Update complete."
    }
} else {
    Write-Host "Current directory is not a Git repository."
}
