<# Runs Python unit tests in multiple environments #>

# Get python.exe paths.
$pyenvs = Get-ChildItem -Path "C:\Python*" -Filter "python.exe" -Recurse
$pyenvs += Get-ChildItem -Path "C:\Program Files\ArcGIS" -Filter "python.exe" -Recurse

# Build the list of modules that will be tested.
$modules_to_test = [string]::Join(" ", @(
    "test_travelerinfo",
    "test_armcalc",
    "test_routeshields"
    )
)

# Initialize a hash table of error codes returned from the test. Only non-zero will be stored.
[System.Diagnostics.Process[]]$jobs = $()

Write-Output "Running unittests..."
# Loop through the paths to the various python executables.
foreach ($pypath in $pyenvs) {
    # Run the unittests and store the error code as a variable.
    $jobs += Start-Process -FilePath $pypath -ArgumentList "-m unittest $modules_to_test" -PassThru
}

Wait-Process -InputObject $jobs

$jobResults = @{}

for ($i = 0; $i -lt $jobs.Count; $i++) {
    $path = $pyenvs[$i]
    $proc = $jobs[$i]
    $jobResults.Add($path.FullName, $proc.ExitCode)
}

# Write-Output $jobResults | Format-Table -AutoSize
return $jobResults