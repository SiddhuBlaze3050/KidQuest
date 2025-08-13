param(
    [switch]$IncludeIntegration
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Ensure-PytestInstalled {
    try {
        python -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('pytest') else 1)" | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Installing pytest..." -ForegroundColor Yellow
            python -m pip install --user pytest --quiet | Out-Null
        }
    } catch {
        Write-Host "Failed to verify/install pytest. Ensure Python and pip are available in PATH." -ForegroundColor Red
        exit 1
    }
}

function Run-Tests {
    if ($IncludeIntegration) {
        # Run all tests including integration; rely on pytest.ini for verbosity and warnings
        $argsList = @('-m', 'integration or not integration', 'backend/test_files')
        python -m pytest @argsList
    } else {
        # Use default runner (pytest.ini controls -v and no warnings)
        python backend/run_all_tests.py
    }
    exit $LASTEXITCODE
}

Ensure-PytestInstalled
Run-Tests


