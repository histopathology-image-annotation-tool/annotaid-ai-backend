# Get the path to the Download-File.ps1 script
$scriptPath = Join-Path -Path $PSScriptRoot -ChildPath "functions.ps1"

# Dot-source the Download-File.ps1 script
. $scriptPath

# Define the MD5 checksum
$md5Checksum="ee942fcbdaa306f46d807e7e3137447d"

# Define the directory path
$directoryPath = "models\"

# Create the directory if it doesn't exist
if (-not (Test-Path $directoryPath)) {
    New-Item -Path $directoryPath -ItemType Directory -Force
}

# NP weights download URL
$url = "https://drive.usercontent.google.com/download?id=1DdQLXbEZOaUm_3IqWj1YfCMK25MA0m5b&confirm=t"

# Download file
$fileName = "NP_model.pt"
$filePath = Join-Path -Path $directoryPath -ChildPath $fileName

$downloadSuccessful = DownloadFile -url $url -filePath $filePath -md5Checksum $md5Checksum

if (-not $downloadSuccessful) {
    Write-Host "The first model weights was downloaded unsuccessfully. Exiting script with error."
    exit 1
}
