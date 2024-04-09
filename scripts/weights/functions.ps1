function DownloadFile {
    param (
        [string]$url,
        [string]$filePath,
        [string]$md5Checksum
    )

    $maxRetries = 5
    $retry = 1

    while ($retry -le $maxRetries) {
        Write-Host "Downloading $url to $filePath..."

        # Disable progressbar, because it slows download
        # https://stackoverflow.com/questions/28682642/powershell-why-is-using-invoke-webrequest-much-slower-than-a-browser-download
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $url -OutFile $filePath
        $ProgressPreference = 'Continue'

        Write-Host "Download completed: $filePath"

        Write-Host "Checking MD5 checksum..."
        $md5 = (Get-FileHash -Path $filePath -Algorithm MD5).Hash.ToLower()

        if ($md5 -eq $md5Checksum) {
            Write-Host "MD5 checksum is correct."
            return $true
        } else {
            Write-Host "MD5 checksum is incorrect. Retrying download..."
            $retry++
        }
    }

    Write-Host "Failed to download $url after $maxRetries attempts."
    return $false
}
