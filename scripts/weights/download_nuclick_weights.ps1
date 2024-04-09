# Get the path to the Download-File.ps1 script
$scriptPath = Join-Path -Path $PSScriptRoot -ChildPath "functions.ps1"

# Dot-source the Download-File.ps1 script
. $scriptPath

# Define the MD5 checksum
$md5Checksum="8ff0c2fd069c303d1c8d7d34a52968e8"

# Define the directory path
$directoryPath = "models\"

# Create the directory if it doesn't exist
if (-not (Test-Path $directoryPath)) {
    New-Item -Path $directoryPath -ItemType Directory -Force
}

# NuClick weights download URL
$url = "https://drive.usercontent.google.com/download?id=1JBK3vWsVC4DxbcStukwnKNZm-vCSLdOb&confirm=t"

# Download file
$fileName = "nuclick_40x.pth"
$filePath = Join-Path -Path $directoryPath -ChildPath $fileName

$downloadSuccessful = DownloadFile -url $url -filePath $filePath -md5Checksum $md5Checksum

if (-not $downloadSuccessful) {
    Write-Host "The first model weights was downloaded unsuccessfully. Exiting script with error."
    exit 1
}
