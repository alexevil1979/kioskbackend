# Update kiosk from GitHub: download main branch ZIP -> C:\kiosk
# Keeps: config\settings.yaml, .env, logs\, media\products\, .venv\
#
#   powershell -ExecutionPolicy Bypass -File scripts\update_kiosk_from_git.ps1
#   powershell -ExecutionPolicy Bypass -File update_kiosk.ps1 -Target C:\kiosk

param(
    [string]$Target = "C:\kiosk",
    [string]$Branch = "main",
    [string]$Repo = "alexevil1979/kioskbackend",
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"

function Write-Step([string]$Text) {
    Write-Host $Text -ForegroundColor Cyan
}

function Copy-Tree([string]$From, [string]$To) {
    if (-not (Test-Path $From)) {
        return
    }
    $parent = Split-Path $To -Parent
    if ($parent -and -not (Test-Path $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    Copy-Item -Path $From -Destination $To -Recurse -Force
}

$Target = [System.IO.Path]::GetFullPath($Target)
if (-not (Test-Path $Target)) {
    New-Item -ItemType Directory -Path $Target -Force | Out-Null
    Write-Host "Created: $Target"
}

$zipUrl = "https://github.com/$Repo/archive/refs/heads/$Branch.zip"
$work = Join-Path $env:TEMP ("kiosk-update-" + [guid]::NewGuid().ToString("N").Substring(0, 8))
$zipPath = Join-Path $work "repo.zip"
$extractDir = Join-Path $work "extract"
$backupDir = Join-Path $work "backup"

New-Item -ItemType Directory -Path $work -Force | Out-Null
New-Item -ItemType Directory -Path $extractDir -Force | Out-Null
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

Write-Step "=== Kiosk update ==="
Write-Host "Target: $Target"
Write-Host "Source: $zipUrl"
Write-Host ""
Write-Host "Close the kiosk app before update (if running)." -ForegroundColor Yellow
Write-Host ""

foreach ($rel in @("config\settings.yaml", ".env")) {
    $src = Join-Path $Target $rel
    if (Test-Path $src) {
        $dst = Join-Path $backupDir $rel
        $dstParent = Split-Path $dst -Parent
        if ($dstParent -and -not (Test-Path $dstParent)) {
            New-Item -ItemType Directory -Path $dstParent -Force | Out-Null
        }
        Copy-Item $src $dst -Force
        Write-Host "Backup: $rel"
    }
}

Write-Step "Downloading..."
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing

Write-Step "Extracting..."
Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force

$srcRoot = Get-ChildItem -Path $extractDir -Directory | Select-Object -First 1
if (-not $srcRoot) {
    throw "Archive root folder not found."
}
Write-Host "Archive folder: $($srcRoot.Name)"

Write-Step "Copying to $Target ..."

foreach ($dir in @("src", "assets", "config\presets", "pic")) {
    Copy-Tree (Join-Path $srcRoot.FullName $dir) (Join-Path $Target $dir)
}

foreach ($file in @(
    "main.py",
    "requirements.txt",
    "run_kiosk.bat",
    ".env.example"
)) {
    $from = Join-Path $srcRoot.FullName $file
    if (Test-Path $from) {
        Copy-Item $from (Join-Path $Target $file) -Force
    }
}

$settingsExample = Join-Path $srcRoot.FullName "config\settings.yaml.example"
if (Test-Path $settingsExample) {
    Copy-Item $settingsExample (Join-Path $Target "config\settings.yaml.example") -Force
}

$terminalRelease = Join-Path $srcRoot.FullName "release\terminal"
if (Test-Path $terminalRelease) {
    foreach ($f in @(
        "install.ps1",
        "install_autostart.ps1",
        "uninstall_autostart.ps1",
        "run_kiosk_silent.bat",
        "update_kiosk.bat",
        "update_kiosk.ps1",
        "README_TERMINAL.txt"
    )) {
        $from = Join-Path $terminalRelease $f
        if (Test-Path $from) {
            Copy-Item $from (Join-Path $Target $f) -Force
        }
    }
}

$updateScript = Join-Path $srcRoot.FullName "scripts\update_kiosk_from_git.ps1"
if (Test-Path $updateScript) {
    Copy-Item $updateScript (Join-Path $Target "update_kiosk.ps1") -Force
}

$docsDir = Join-Path $Target "docs"
if (-not (Test-Path $docsDir)) {
    New-Item -ItemType Directory -Path $docsDir -Force | Out-Null
}
foreach ($doc in @(
    "INSTALL_TERMINAL_WIN10.md",
    "DEPLOYMENT.md",
    "CONFIGURATION.md",
    "START_CHECKLIST.md",
    "SETUP_NUC_PRINTER_LAN.md",
    "api\ENV.md"
)) {
    $from = Join-Path $srcRoot.FullName "docs\$doc"
    if (Test-Path $from) {
        $dstDir = Join-Path $docsDir (Split-Path $doc -Parent)
        if ($dstDir -and -not (Test-Path $dstDir)) {
            New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
        }
        Copy-Item $from (Join-Path $docsDir $doc) -Force
    }
}

@("logs", "media\products") | ForEach-Object {
    $p = Join-Path $Target $_
    if (-not (Test-Path $p)) {
        New-Item -ItemType Directory -Path $p -Force | Out-Null
    }
}

foreach ($rel in @("config\settings.yaml", ".env")) {
    $backup = Join-Path $backupDir $rel
    $dest = Join-Path $Target $rel
    if (Test-Path $backup) {
        $destParent = Split-Path $dest -Parent
        if ($destParent -and -not (Test-Path $destParent)) {
            New-Item -ItemType Directory -Path $destParent -Force | Out-Null
        }
        Copy-Item $backup $dest -Force
        Write-Host "Restored: $rel"
    }
}

if (-not $SkipInstall) {
    $install = Join-Path $Target "install.ps1"
    if (Test-Path $install) {
        Write-Step "Running install.ps1 (pip)..."
        & powershell -NoProfile -ExecutionPolicy Bypass -File $install
        if ($LASTEXITCODE -ne 0) {
            throw "install.ps1 failed with exit code $LASTEXITCODE"
        }
    } else {
        Write-Host "install.ps1 not found, skip pip." -ForegroundColor Yellow
    }
}

Remove-Item $work -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Green
Write-Host "Run: $Target\run_kiosk.bat"
