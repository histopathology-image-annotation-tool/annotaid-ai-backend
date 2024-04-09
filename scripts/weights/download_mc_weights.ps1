# Get the path to the Download-File.ps1 script
$scriptPath = Join-Path -Path $PSScriptRoot -ChildPath "functions.ps1"

# Dot-source the Download-File.ps1 script
. $scriptPath

# Define the MD5 checksums
$md5ChecksumFirstStage = "b925a51aa6acaf889f6104f239c1c0a5"
$md5ChecksumSecondStage = "50dbb9d396ef71cb660b1c0b7961cf62"

# Define the directory path
$directoryPath = "models\"

# Create the directory if it doesn't exist
if (-not (Test-Path $directoryPath)) {
    New-Item -Path $directoryPath -ItemType Directory -Force
}

# MC weights download URL
$url_first_stage = "https://drive.usercontent.google.com/download?id=1DDEfvJvhgjh3PXHRHW7pql_Lcmodkpri&confirm=t"
$url_second_stage = "https://drive.usercontent.google.com/download?id=1r8S42ksZgx0Cr1maBAaeQbPTOeUEWvFy&confirm=t"

$fileNameFirstStage = "MC_first_stage.pt"
$fileFirstStagePath = Join-Path -Path $directoryPath -ChildPath $fileNameFirstStage

$fileNameSecondStage = "MC_second_stage.pt"
$fileSecondStagePath = Join-Path -Path $directoryPath -ChildPath $fileNameSecondStage

# Download the first stage weights
$downloadFirstStageSuccessful = DownloadFile -url $url_first_stage -filePath $fileFirstStagePath -md5Checksum $md5ChecksumFirstStage

if (-not $downloadFirstStageSuccessful) {
    Write-Host "The first model weights was downloaded unsuccessfully. Exiting script with error."
    exit 1
}

$downloadSecondStageSuccessful = DownloadFile -url $url_second_stage -filePath $fileSecondStagePath -md5Checksum $md5ChecksumSecondStage

if (-not $downloadSecondStageSuccessful) {
    Write-Host "The second model weights was downloaded unsuccessfully. Exiting script with error."
    exit 1
}
