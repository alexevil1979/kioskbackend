# Сборка ZIP-пакета для установки на терминал Windows 10.
# Запуск из корня репозитория:
#   powershell -ExecutionPolicy Bypass -File scripts\build_terminal_package.ps1

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Date = Get-Date -Format "yyyyMMdd"
$Name = "kiosk-terminal-$Date"
$DistRoot = Join-Path $ProjectRoot "dist"
$OutDir = Join-Path $DistRoot $Name
$ZipPath = Join-Path $DistRoot "$Name.zip"

Write-Host "=== Build terminal package ===" -ForegroundColor Cyan
Write-Host "Source: $ProjectRoot"
Write-Host "Output: $ZipPath"

if (Test-Path $OutDir) {
    Remove-Item $OutDir -Recurse -Force
}
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

function Copy-Tree {
    param([string]$Relative)
    $src = Join-Path $ProjectRoot $Relative
    $dst = Join-Path $OutDir $Relative
    if (Test-Path $src) {
        $parent = Split-Path $dst -Parent
        if (-not (Test-Path $parent)) {
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
        }
        Copy-Item -Path $src -Destination $dst -Recurse -Force
    }
}

# Kod i resursy (pic/ — berry-*.webp dlya kartochek kataloga)
foreach ($dir in @("src", "assets", "config\presets", "pic")) {
    Copy-Tree $dir
}

# Точки входа
foreach ($file in @("main.py", "requirements.txt", "run_kiosk.bat", ".env.example")) {
    Copy-Item (Join-Path $ProjectRoot $file) (Join-Path $OutDir $file) -Force
}

# Пример настроек (не боевой settings.yaml)
Copy-Item (Join-Path $ProjectRoot "config\settings.yaml.example") (Join-Path $OutDir "config\settings.yaml.example") -Force

# Пустые рабочие каталоги
New-Item -ItemType Directory -Path (Join-Path $OutDir "logs") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $OutDir "media\products") -Force | Out-Null
Copy-Item (Join-Path $ProjectRoot "media\products\.gitkeep") (Join-Path $OutDir "media\products\.gitkeep") -Force -ErrorAction SilentlyContinue

# Скрипты установки (в корень пакета)
$TerminalRelease = Join-Path $ProjectRoot "release\terminal"
foreach ($f in @(
    "install.ps1",
    "install_autostart.ps1",
    "uninstall_autostart.ps1",
    "run_kiosk_silent.bat",
    "update_kiosk.bat",
    "README_TERMINAL.txt"
)) {
    Copy-Item (Join-Path $TerminalRelease $f) (Join-Path $OutDir $f) -Force
}

Copy-Item (Join-Path $ProjectRoot "scripts\update_kiosk_from_git.ps1") (Join-Path $OutDir "update_kiosk.ps1") -Force

# Документация для монтажа
New-Item -ItemType Directory -Path (Join-Path $OutDir "docs") -Force | Out-Null
foreach ($doc in @(
    "INSTALL_TERMINAL_WIN10.md",
    "DEPLOYMENT.md",
    "CONFIGURATION.md",
    "START_CHECKLIST.md",
    "SETUP_NUC_PRINTER_LAN.md",
    "api\ENV.md"
)) {
    $src = Join-Path (Join-Path $ProjectRoot "docs") $doc
    if (Test-Path $src) {
        $dstDir = Join-Path (Join-Path $OutDir "docs") (Split-Path $doc -Parent)
        if ($dstDir -and -not (Test-Path $dstDir)) {
            New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
        }
        Copy-Item $src (Join-Path (Join-Path $OutDir "docs") $doc) -Force
    }
}

# Манифест версии
$commit = ""
try {
    $commit = (git -C $ProjectRoot rev-parse --short HEAD 2>$null)
} catch { }
@"
kiosk-terminal-package
built: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
git: $commit
python: 3.11+
os: Windows 10
"@ | Set-Content (Join-Path $OutDir "BUILD_INFO.txt") -Encoding UTF8

# ZIP
if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
}
Compress-Archive -Path $OutDir -DestinationPath $ZipPath -CompressionLevel Optimal

$sizeMb = [math]::Round((Get-Item $ZipPath).Length / 1MB, 2)
Write-Host ""
Write-Host "Done: $ZipPath ($sizeMb MB)" -ForegroundColor Green
Write-Host "Folder: $OutDir"
