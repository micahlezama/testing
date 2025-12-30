# PowerShell script to download embedded Python, extract it, and install dependencies
# Define the URL for the embedded Python zip file (adjust version as needed)
$pythonUrl = "https://drive.google.com/uc?export=download&id=1I8HQiQWW3df0PaLSlIda_ReUeEqTHXWG&confirm=t"

# Define paths
$zipPath = Join-Path $PSScriptRoot "python.zip"
$extractPath = $PSScriptRoot
$requirementsPath = Join-Path $PSScriptRoot "requirements.txt"

# Find the Python executable
$pythonExe = Join-Path $extractPath "python\python.exe"
$globpy = $false

# Check if global python version is 3.9
if (python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" | Select-String -Pattern '3.9' -Quiet) {
    $pythonExe = 'python'
    $globpy = $true
}
else {
    # Check if Python is already downloaded and extracted
    if (Test-Path $pythonExe) {
        Write-Host "Python is already downloaded!"
    } else {
        try {
            # Download the Python zip file
            Write-Host "Downloading Python..."

            $FileID = "1I8HQiQWW3df0PaLSlIda_ReUeEqTHXWG"
            # set protocol to tls version 1.2
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

            # Download the Virus Warning into _tmp.txt
            Invoke-WebRequest -Uri "https://drive.google.com/uc?export=download&id=$FileID" -OutFile "_tmp.txt" -SessionVariable googleDriveSession

            $htmlContent = Get-Content "_tmp.txt"

            # Regex pattern to match the uuid value
            $pattern = '<input type="hidden" name="uuid" value="(.+?)">'

            # Perform regex match to find the uuid value
            if ($htmlContent -match $pattern) {
                $uuidValue = $matches[1] # Captured group 1 contains the uuid value
                Write-Output "UUID Value: $uuidValue"
            } else {
                Write-Output "UUID value not found."
            }

            # Delete _tmp.txt
            Remove-Item "_tmp.txt"

            # Download the real file

            Invoke-WebRequest -Uri "https://drive.usercontent.google.com/download?id=$FileID&export=download&confirm=t&uuid=$uuidValue" -OutFile $zipPath -WebSession $googleDriveSession
            Write-Host "Download completed successfully."
        } catch {
            Write-Error "Failed to download Python zip file: $_"
            exit 1
        }

        try {
            # Extract the zip file
            Write-Host "Extracting Python..."
            Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force -ErrorAction Stop
            Write-Host "Extraction completed successfully."
        } catch {
            Write-Error "Failed to extract Python zip file"
            exit 1
        }
    }
}

# Check if Python executable exists
if ((-not (Test-Path $pythonExe)) -and (-not ($globpy))) {
    Write-Error "Python executable not found!"
    exit 1
}

# Install dependencies using the downloaded Python's pip
Write-Host "Installing dependencies..."


try {
    Write-Host "Upgrading pip..."
    & $pythonExe -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        throw "Pip upgrade failed with exit code $LASTEXITCODE"
    }
    Write-Host "Pip upgrade completed successfully."
} catch {
    Write-Error "Failed to upgrade pip"
    exit 1
}

try {
    Write-Host "Installing packages from requirements.txt..."
    & $pythonExe -m pip install -r $requirementsPath
    if ($LASTEXITCODE -ne 0) {
        throw "Pip install failed with exit code $LASTEXITCODE"
    }
    Write-Host "Package installation completed successfully."
} catch {
    Write-Error "Failed to install dependencies"
    exit 1
}

# Optional: Clean up the zip file
Write-Host "Cleaning up..."
Remove-Item $zipPath -ErrorAction SilentlyContinue

Write-Host "Initialization complete! Starting the bot..."


& $pythonExe auxil.py
