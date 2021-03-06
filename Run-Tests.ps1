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
[System.IO.DirectoryInfo]$test_output_dir = "$env:TEMP\test_output"
New-Item $test_output_dir -ItemType Directory -ErrorAction Ignore | Write-Host

# Name for progress activity
$activity = "Running unittests"
Write-Progress $activity

# Loop through the paths to the various python executables.
# TODO: Update the progress meter as each process finishes.
$i = 0
foreach ($pypath in $pyenvs) {
    # Run the unittests and store the error code as a variable.
    $jobs += Start-Process -FilePath $pypath.FullName -ArgumentList "-m unittest discover --start-directory src" -PassThru -NoNewWindow -RedirectStandardError "$test_output_dir\Error$i.txt"
    $i++
}

# Wait for all of the unit test processes to finish.
Wait-Process -InputObject $jobs

# Stop the progress meter now that the processes are finished.
Write-Progress $activity -Completed

# Create the TestResult class
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

# Initialize output result list.
[TestResult[]]$jobResults = $()

# Loop through the process objects and collect the results.
for ($i = 0; $i -lt $jobs.Count; $i++) {
    $path = $pyenvs[$i]
    $proc = $jobs[$i]
    $errorFile = "$test_output_dir\Error$i.txt"

    # If there was an error message, read the result to a file.
    [string]$msg = $null
    if ($proc.ExitCode -ne 0) {
        $msg = Get-Content $errorFile -Raw
    }
    # Now that the error message text has been stored (or ignored if there was no error),
    # the corresponding file can be deleted.
    Remove-Item $errorFile

    $result = New-Object TestResult @($path.FullName, $proc.ExitCode, $msg)
    $jobResults += $result
}

# Remove the directory that had the test output files.
Remove-Item $test_output_dir

return $jobResults