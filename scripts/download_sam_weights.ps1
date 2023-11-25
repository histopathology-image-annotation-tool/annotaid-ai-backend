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

Write-Output "Downloading $url to $filePath..."

# Disable progressbar, because it slows dowload
# https://stackoverflow.com/questions/28682642/powershell-why-is-using-invoke-webrequest-much-slower-than-a-browser-download
$ProgressPreference = 'SilentlyContinue'
Invoke-WebRequest -Uri $url -OutFile $filePath

$ProgressPreference = 'Continue'

Write-Output "Download completed: $filePath"
