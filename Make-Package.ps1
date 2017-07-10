<#
.SYNOPSIS
    Creates the Python package files
#>

$pythons = Get-ChildItem "$env:ProgramFiles\ArcGIS\Pro\bin\Python" "python.exe" -Recurse | Where-Object { $_.FullName -notlike "*pkgs*" }

if ($pythons.Length -lt 1) {
    Write-Error "No python.exe found."
}
$python = $pythons[0].FullName

Write-Progress "Creating Package files" -CurrentOperation "Creating source distribution..." -PercentComplete 0
Start-Process $python "setup.py sdist" -Wait -WindowStyle Hidden
Write-Progress "Creating Package files" -CurrentOperation "Creating Universal Wheel..." -PercentComplete 50
Start-Process $python "setup.py bdist_wheel --universal" -Wait -WindowStyle Hidden
