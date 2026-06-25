# Kiosk install on Windows 10 (terminal / NUC).
#   Set-ExecutionPolicy -Scope Process Bypass -Force
#   .\install.ps1
#   .\install.ps1 -Autostart
#   .\install.ps1 -Autostart -Preset pos_sbp

param(
    [switch]$Autostart,
    [ValidateSet("none", "pos_sbp", "aqsi", "pos_printer")]
    [string]$Preset = "none"
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

function Invoke-PythonVersionCheck {
    param(
        [string]$Exe,
        [string[]]$PrefixArgs = @()
    )
    $code = "import sys; print('{}.{}'.format(sys.version_info.major, sys.version_info.minor))"
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    $lines = @()
    try {
        $lines = @(& $Exe @($PrefixArgs + @("-c", $code)) 2>$null)
    } catch {
        return $null
    } finally {
        $ErrorActionPreference = $prev
    }
    if ($null -ne $LASTEXITCODE -and $LASTEXITCODE -ne 0) {
        return $null
    }
    $ver = ($lines | Where-Object { $_ -match '^\d+\.\d+$' } | Select-Object -Last 1)
    if (-not $ver) {
        return $null
    }
    try {
        if ([version]$ver.Trim() -ge [version]"3.11") {
            return @{ Exe = $Exe; Args = $PrefixArgs }
        }
    } catch {
        return $null
    }
    return $null
}

function Find-Python {
    foreach ($spec in @(
            @{ Exe = "py"; Args = @("-3") },
            @{ Exe = "python"; Args = @() }
        )) {
        $found = Invoke-PythonVersionCheck -Exe $spec.Exe -PrefixArgs $spec.Args
        if ($found) {
            return $found
        }
    }
    return $null
}

function Invoke-PythonCommand {
    param(
        [hashtable]$Py,
        [string[]]$CommandArgs
    )
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    try {
        & $Py.Exe @($Py.Args + $CommandArgs)
        if ($null -ne $LASTEXITCODE -and $LASTEXITCODE -ne 0) {
            throw "Command failed (exit $LASTEXITCODE): $($Py.Exe) $($Py.Args -join ' ') $($CommandArgs -join ' ')"
        }
    } finally {
        $ErrorActionPreference = $prev
    }
}

Write-Host "=== Kiosk install ===" -ForegroundColor Cyan
Write-Host "Folder: $Root"

$py = Find-Python
if (-not $py) {
    Write-Host "ERROR: Python 3.11+ required (https://www.python.org/downloads/windows/)" -ForegroundColor Red
    Write-Host "Enable Add python.exe to PATH during install."
    exit 1
}
Write-Host "Python: $($py.Exe) $($py.Args -join ' ')"

$settingsExample = Join-Path $Root "config\settings.yaml.example"
$settings = Join-Path $Root "config\settings.yaml"
if (-not (Test-Path $settings)) {
    Copy-Item $settingsExample $settings
    Write-Host "Created config\settings.yaml from example."
} else {
    Write-Host "config\settings.yaml exists - kept."
}

$envExample = Join-Path $Root ".env.example"
$envFile = Join-Path $Root ".env"
if (-not (Test-Path $envFile)) {
    Copy-Item $envExample $envFile
    Write-Host "Created .env from example - fill API keys."
} else {
    Write-Host ".env exists - kept."
}

@("logs", "media\products") | ForEach-Object {
    $p = Join-Path $Root $_
    if (-not (Test-Path $p)) {
        New-Item -ItemType Directory -Path $p -Force | Out-Null
    }
}

if ($Preset -ne "none") {
    $presetFile = Join-Path $Root "config\presets\mode_$Preset.yaml"
    if (Test-Path $presetFile) {
        Write-Host ""
        Write-Host "Preset mode_$Preset.yaml - merge sections into config\settings.yaml manually" -ForegroundColor Yellow
        Write-Host "  See docs\INSTALL_TERMINAL_WIN10.md"
    }
}

$venv = Join-Path $Root ".venv"
$venvPy = Join-Path $venv "Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    Write-Host "Creating virtual environment..."
    Invoke-PythonCommand -Py $py -CommandArgs @("-m", "venv", $venv)
}
Write-Host "Installing dependencies (pip)..."
& $venvPy -m pip install --upgrade pip --quiet 2>$null
if ($LASTEXITCODE -ne 0) {
    throw "pip upgrade failed (exit $LASTEXITCODE)"
}
& $venvPy -m pip install -r (Join-Path $Root "requirements.txt")
if ($LASTEXITCODE -ne 0) {
    throw "pip install failed (exit $LASTEXITCODE)"
}

Write-Host "Checking PyQt6..."
$prev = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
& $venvPy -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')" 2>$null
$ErrorActionPreference = $prev
if ($LASTEXITCODE -ne 0) {
    throw "PyQt6 check failed (exit $LASTEXITCODE)"
}

if ($Autostart) {
    & (Join-Path $Root "install_autostart.ps1")
}

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Green
Write-Host "1. Edit config\settings.yaml and .env (CRM, payment keys)."
Write-Host "2. Run: run_kiosk.bat  or  run_kiosk_silent.bat (no console)."
Write-Host "3. Full guide: docs\INSTALL_TERMINAL_WIN10.md"
if (-not $Autostart) {
    Write-Host "4. Autostart: .\install.ps1 -Autostart"
}
