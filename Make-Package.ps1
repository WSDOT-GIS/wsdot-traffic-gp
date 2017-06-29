<#
.SYNOPSIS
    Creates the Python package files
#>

Write-Host "Creating source distribution..."
python setup.py sdist
Write-Host "Creating Universal Wheel..."
python setup.py bdist_wheel --universal