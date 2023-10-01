# Define target directories for removal
$torDir = "$env:USERPROFILE\tor2tor\Tor"
$geckoDir = "$env:USERPROFILE\tor2tor\GeckoDriver"

# Function to remove directory
function RemoveDir([string]$dirPath) {
    if (Test-Path $dirPath) {
        Remove-Item -Path $dirPath -Recurse -Force
        Write-Host "Removed directory: $dirPath"
    } else {
        Write-Host "Directory $dirPath does not exist."
    }
}

# Remove Tor directory
RemoveDir $torDir

# Remove GeckoDriver directory
RemoveDir $geckoDir

# Remove the geckodriver directory from PATH
$pathEnv = [Environment]::GetEnvironmentVariable("PATH", [EnvironmentVariableTarget]::User)
$newPath = ($pathEnv -split ";" | Where-Object { $_ -ne $geckoDir }) -join ";"
[Environment]::SetEnvironmentVariable("PATH", $newPath, [EnvironmentVariableTarget]::User)
Write-Host "Removed GeckoDriver directory from PATH."

# Uninstall tor2tor Python package
pip uninstall tor2tor -y

Write-Host "Cleanup complete."
