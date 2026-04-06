param(
    [string]$PythonExe = "python",
    [switch]$UseVenvPython
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$configPath = Join-Path $repoRoot "config\operator_api.local.json"
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

if ($UseVenvPython) {
    if (-not (Test-Path $venvPython)) {
        throw "Requested -UseVenvPython but .venv python was not found at $venvPython"
    }
    $PythonExe = $venvPython
}

if (-not (Test-Path $configPath)) {
    throw "Missing operator API config at $configPath. Copy config\\operator_api_config.example.json to config\\operator_api.local.json first."
}

Push-Location $repoRoot
try {
    $existingPythonPath = $env:PYTHONPATH
    $srcPath = Join-Path $repoRoot "src"
    if ([string]::IsNullOrWhiteSpace($existingPythonPath)) {
        $env:PYTHONPATH = $srcPath
    }
    else {
        $env:PYTHONPATH = "$srcPath;$existingPythonPath"
    }

    & $PythonExe "src\cli\run_operator_api.py"
}
finally {
    Pop-Location
}
