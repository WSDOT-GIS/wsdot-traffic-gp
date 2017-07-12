<#
.SYNOPSIS
    Runs Python unit tests in multiple environments
.OUTPUTS
    Array of test results. Each item has
        * Python Path
        * Test return code
        * Error message. (Only non-zero return codes will have a message)
#>

# Get python.exe paths.
[System.IO.FileInfo[]]$pyenvs = Get-Item "C:\Python*\**\python.exe" # Python 2.x (ArcGIS Desktop)
# Get the Python 3.X ArcGIS Pro Python executables, excluding the ones in the /pkgs/ folder.
$pyenvs += Get-ChildItem "$env:ProgramFiles\ArcGIS" "python.exe" -File -Recurse | Where-Object { $_.FullName -notlike "*pkgs*" }

# Initialize a list of Process objects.
[System.Diagnostics.Process[]]$jobs = $()

# Create directory for test output
$test_output_dir = "test_output"
New-Item $test_output_dir -ItemType Directory -ErrorAction Ignore | Write-Host

# Name for progress activity
$activity = "Running unittests"
Write-Progress $activity

# Loop through the paths to the various python executables.
$i = 0
foreach ($pypath in $pyenvs) {
    # Run the unittests and store the error code as a variable.
    $jobs += Start-Process -FilePath $pypath.FullName -ArgumentList "-m unittest discover --start-directory src" -PassThru -NoNewWindow -RedirectStandardError "test_output\Error$i.txt"
    $i++
}

Wait-Process -InputObject $jobs

Write-Progress $activity -Completed

class TestResult {
    [System.IO.FileInfo]$PythonPath
    [int]$ReturnCode
    [string]$ErrorMessage
    TestResult($python, $returnCode, $errorMessage) {
        $this.PythonPath = $python
        $this.ReturnCode = $returnCode
        $this.ErrorMessage = $errorMessage
    }
}

[TestResult[]]$jobResults = $()

for ($i = 0; $i -lt $jobs.Count; $i++) {
    $path = $pyenvs[$i]
    $proc = $jobs[$i]
    $errorFile = ".\test_output\Error$i.txt"

    [string]$msg = $null
    if ($proc.ExitCode -ne 0) {
        $msg = Get-Content $errorFile -Raw
    }
    Remove-Item $errorFile
    $result = New-Object TestResult @($path.FullName, $proc.ExitCode, $msg)
    $jobResults += $result
}

Remove-Item $test_output_dir

return $jobResults