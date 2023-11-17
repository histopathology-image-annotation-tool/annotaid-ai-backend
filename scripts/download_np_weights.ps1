# Define the directory path
$directoryPath = "models\"

# Create the directory if it doesn't exist
if (-not (Test-Path $directoryPath)) {
    New-Item -Path $directoryPath -ItemType Directory -Force
}

# NP weights download URL
$url = "https://docs.google.com/uc?export=download&id=1DdQLXbEZOaUm_3IqWj1YfCMK25MA0m5b&confirm=t"

# Download file
$fileName = "NP_model.pt"
$filePath = Join-Path -Path $directoryPath -ChildPath $fileName

Write-Output "Downloading $url to $filePath..."

# Disable progressbar, because it slows dowload
# https://stackoverflow.com/questions/28682642/powershell-why-is-using-invoke-webrequest-much-slower-than-a-browser-download
$ProgressPreference = 'SilentlyContinue'
Invoke-WebRequest -Uri $url -OutFile $filePath

$ProgressPreference = 'Continue'

Write-Output "Download completed: $filePath"
