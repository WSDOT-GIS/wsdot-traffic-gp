<#
.SYNOPSIS
    Creates the Python package files
#>

Write-Host "Creating source distribution..." -ForegroundColor Green
python setup.py sdist
Write-Host "Creating Universal Wheel..." -ForegroundColor Green
python setup.py bdist_wheel --universal