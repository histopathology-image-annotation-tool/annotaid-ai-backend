# Define the directory path
$directoryPath = "models\"

# Create the directory if it doesn't exist
if (-not (Test-Path $directoryPath)) {
    New-Item -Path $directoryPath -ItemType Directory -Force
}

# NuClick weights download URL
$url_first_stage = "https://docs.google.com/uc?export=download&id=1DDEfvJvhgjh3PXHRHW7pql_Lcmodkpri&confirm=t"
$url_second_stage = "https://docs.google.com/uc?export=download&id=1r8S42ksZgx0Cr1maBAaeQbPTOeUEWvFy&confirm=t"


$fileNameFirstStage = "MC_first_stage.pt"
$fileFirstStagePath = Join-Path -Path $directoryPath -ChildPath $fileNameFirstStage

$fileNameSecondStage = "MC_second_stage.pt"
$fileSecondStagePath = Join-Path -Path $directoryPath -ChildPath $fileNameSecondStage

# Disable progressbar, because it slows dowload
# https://stackoverflow.com/questions/28682642/powershell-why-is-using-invoke-webrequest-much-slower-than-a-browser-download
$ProgressPreference = 'SilentlyContinue'

# Download first-stage model
Write-Output "Downloading $url_first_stage to $fileFirstStagePath..."
Invoke-WebRequest -Uri $url_first_stage -OutFile $fileFirstStagePath

Write-Output "Download completed: $fileFirstStagePath"

# Download second-stage model
Write-Output "Downloading $url_second_stage to $fileSecondStagePath"
Invoke-WebRequest -Uri $url_second_stage -OutFile $fileSecondStagePath

Write-Output "Download completed: $fileSecondStagePath"

$ProgressPreference = 'Continue'
