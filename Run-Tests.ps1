<# Runs Python unit tests in multiple environments #>

# Get python.exe paths.
[System.IO.FileInfo[]]$pyenvs = Get-Item "C:\Python*\**\python.exe"
$pyenvs += Get-ChildItem -Path "C:\Program Files\ArcGIS\Pro\bin\Python\envs" -Filter "python.exe" -Recurse

# Initialize a hash table of error codes returned from the test. Only non-zero will be stored.
[System.Diagnostics.Process[]]$jobs = $()

Remove-Item "test_output\*"

$activity = "Running unittests"
Write-Progress  $activity
# Loop through the paths to the various python executables.
$i = 0
foreach ($pypath in $pyenvs) {
    # Run the unittests and store the error code as a variable.
    $jobs += Start-Process -FilePath $pypath.FullName -ArgumentList "-m unittest discover --start-directory src" -PassThru -NoNewWindow -RedirectStandardError "test_output\Error$i.txt"
    $i++
}

Wait-Process -InputObject $jobs

Write-Progress $activity -Completed

$jobResults = @{}

for ($i = 0; $i -lt $jobs.Count; $i++) {
    $path = $pyenvs[$i]
    $proc = $jobs[$i]
    if ($proc.ExitCode -eq 0) {
        Remove-Item ".\test_output\Error$i.txt"
    }
    $jobResults.Add($path.FullName, $proc.ExitCode)
}

return $jobResults