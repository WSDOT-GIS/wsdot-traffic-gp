<#
.SYNOPSIS
    Runs a Python script in the ArcGIS Pro environment
.DESCRIPTION
    Runs a Python script in the ArcGIS Pro environment.
.EXAMPLE
    PS C:\> \.Run-PythonInArcGisProEnv.ps1 myscript.py
    Runs the myscript.py script in the ArcGIS Pro Python environment.
#>

Param(
    # The Python script to be executed.
    [System.IO.FileInfo]
    $PythonScript="creategdb.py"
)

# Find the ArcGIS Pro Python environment (defined by Conda).
[System.IO.DirectoryInfo]$ProEnvFolder = "$env:ProgramFiles\ArcGIS\Pro\bin\Python\envs\arcgispro-py3"
# Get the Python executable from that folder.
[System.IO.FileInfo]$pythonexe = Get-ChildItem $ProEnvFolder "python.exe"

# Start the Python script's execution, using the full path to the Python exe.
Start-Process -FilePath $pythonexe.FullName -ArgumentList $PythonScript -NoNewWindow -PassThru -Wait