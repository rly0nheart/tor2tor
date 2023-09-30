# Define URLs for Tor Expert Bundle and GeckoDriver
$torURL = "https://archive.torproject.org/tor-package-archive/torbrowser/12.5.6/tor-expert-bundle-12.5.6-windows-x86_64.tar.gz"
$geckoURL = "https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-win64.zip"

# Define target directories for installation
$torDir = "$env:USERPROFILE\Tor"
$geckoDir = "$env:USERPROFILE\GeckoDriver"

# Function to download a file
function DownloadFile([string]$url, [string]$path) {
    Invoke-WebRequest -Uri $url -OutFile $path
}

# Check if Tor directory exists, if not create and download
if (-Not (Test-Path $torDir)) {
    New-Item -Path $torDir -ItemType Directory
    Write-Host "Downloading Tor..."
    DownloadFile $torURL "$torDir\tor.tar.gz"

    # Unpacking the Tor archive
    tar -xf "$torDir\tor.tar.gz" -C $torDir
    Remove-Item "$torDir\tor.tar.gz"
}

# Check if GeckoDriver directory exists, if not create and download
if (-Not (Test-Path $geckoDir)) {
    New-Item -Path $geckoDir -ItemType Directory
    Write-Host "Downloading GeckoDriver..."
    DownloadFile $geckoURL "$geckoDir\geckodriver.zip"

    # Unzipping the GeckoDriver
    Expand-Archive -Path "$geckoDir\geckodriver.zip" -DestinationPath $geckoDir
    Remove-Item "$geckoDir\geckodriver.zip"
}

pip install .

# Optionally, add the directories to your PATH (if you want)
# [Environment]::SetEnvironmentVariable("PATH", [Environment]::GetEnvironmentVariable("PATH", [EnvironmentVariableTarget]::User) + ";$torDir;$geckoDir", [EnvironmentVariableTarget]::User)

Write-Host "Setup complete."
