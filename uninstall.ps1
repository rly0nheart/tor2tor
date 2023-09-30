# Define target directories for removal
$torDir = "$env:USERPROFILE\Tor"
$geckoDir = "$env:USERPROFILE\GeckoDriver"

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

# Optionally, remove the directories from your PATH
$removeFromPath = Read-Host "Do you want to remove these directories from PATH? (y/n)"
if ($removeFromPath -eq 'y') {
    $pathEnv = [Environment]::GetEnvironmentVariable("PATH", [EnvironmentVariableTarget]::User)
    $newPath = ($pathEnv -split ";" | Where-Object { $_ -ne $torDir -and $_ -ne $geckoDir }) -join ";"
    [Environment]::SetEnvironmentVariable("PATH", $newPath, [EnvironmentVariableTarget]::User)
    Write-Host "Removed directories from PATH."
} else {
    Write-Host "Skipped removing directories from PATH."
}

pip uninstall tor2tor -y
Write-Host "Cleanup complete."
