# Define URLs for Tor Expert Bundle and GeckoDriver
$torURL = "https://archive.torproject.org/tor-package-archive/torbrowser/13.0/tor-expert-bundle-13.0-windows-x86_64.tar.gz"
$geckoURL = "https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-win64.zip"

# Define target directories for installation
$torDir = "$env:USERPROFILE\tor2tor\Tor"
$geckoDir = "$env:USERPROFILE\tor2tor\GeckoDriver"

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

# Add the geckodriver directory to PATH
[Environment]::SetEnvironmentVariable("PATH", [Environment]::GetEnvironmentVariable("PATH", [EnvironmentVariableTarget]::User) + ";$geckoDir", [EnvironmentVariableTarget]::User)

pip install .
Write-Host "Setup complete."
