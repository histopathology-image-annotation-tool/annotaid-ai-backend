# Get the name of the current script
$current_script_name = $MyInvocation.MyCommand.Name
$current_directory = Split-Path $MyInvocation.MyCommand.Path

# Loop over all .ps1 files in the current directory
Get-ChildItem -Path $current_directory -Filter "*.ps1" | ForEach-Object {
    # If the file is not the current script, execute it
    if ($_.Name -ne $current_script_name) {
        Write-Output "Executing: $($_.FullName)"
        & $_.FullName
    }
}
