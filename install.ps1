# Define URLs for Tor Expert Bundle and GeckoDriver
$torURL = "https://archive.torproject.org/tor-package-archive/torbrowser/12.5.6/tor-expert-bundle-12.5.6-windows-x86_64.tar.gz"

# Define target directory for installation
$torDir = "$env:USERPROFILE\tor2tor\Tor"

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


pip install .
Write-Host "Setup complete."
