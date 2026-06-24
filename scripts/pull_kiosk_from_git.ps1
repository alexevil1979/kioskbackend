# Скачать ZIP ветки main с GitHub и распаковать в папку киоск (перезапись файлов из архива).
#
#   powershell -ExecutionPolicy Bypass -File scripts\pull_kiosk_from_git.ps1
#   powershell -ExecutionPolicy Bypass -File scripts\pull_kiosk_from_git.ps1 -Target C:\kiosk

param(
    [string]$Target = "",
    [string]$Branch = "main",
    [string]$Repo = "alexevil1979/kioskbackend"
)

$ErrorActionPreference = "Stop"

function Write-Step([string]$Text) {
    Write-Host $Text -ForegroundColor Cyan
}

if (-not $Target) {
    $Target = Split-Path $PSScriptRoot -Parent
}
$Target = [System.IO.Path]::GetFullPath($Target)

if (-not (Test-Path $Target)) {
    New-Item -ItemType Directory -Path $Target -Force | Out-Null
    Write-Host "Created: $Target"
}

$zipUrl = "https://github.com/$Repo/archive/refs/heads/$Branch.zip"
$work = Join-Path $env:TEMP ("kiosk-pull-" + [guid]::NewGuid().ToString("N").Substring(0, 8))
$zipPath = Join-Path $work "repo.zip"
$extractDir = Join-Path $work "extract"

New-Item -ItemType Directory -Path $work -Force | Out-Null
New-Item -ItemType Directory -Path $extractDir -Force | Out-Null

Write-Step "=== Pull kiosk from GitHub ==="
Write-Host "Target: $Target"
Write-Host "Source: $zipUrl"
Write-Host ""
Write-Host "Files from the archive will overwrite existing ones in the target folder." -ForegroundColor Yellow
Write-Host "Local-only files (.venv, .env, logs, media) are kept if not in the archive." -ForegroundColor Yellow
Write-Host ""

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
Get-ChildItem -Path $srcRoot.FullName -Force | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $Target $_.Name) -Recurse -Force
}

Remove-Item $work -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Green
Write-Host "Folder: $Target"
