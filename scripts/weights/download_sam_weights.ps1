# Get the path to the Download-File.ps1 script
$scriptPath = Join-Path -Path $PSScriptRoot -ChildPath "functions.ps1"

# Dot-source the Download-File.ps1 script
. $scriptPath

# Define the MD5 checksum
$md5Checksum="01ec64d29a2fca3f0661936605ae66f8"

# Define the directory path
$directoryPath = "models\"

# Create the directory if it doesn't exist
if (-not (Test-Path $directoryPath)) {
    New-Item -Path $directoryPath -ItemType Directory -Force
}

# NP weights download URL
$url = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"

# Download file
$fileName = "sam_vit_b_01ec64.pth"
$filePath = Join-Path -Path $directoryPath -ChildPath $fileName

$downloadSuccessful = DownloadFile -url $url -filePath $filePath -md5Checksum $md5Checksum

if (-not $downloadSuccessful) {
    Write-Host "The first model weights was downloaded unsuccessfully. Exiting script with error."
    exit 1
}
