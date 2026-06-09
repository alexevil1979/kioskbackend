# Установка киоска «Сады Коломны» на Windows 10 (терминал / NUC).
# Запуск: PowerShell от имени пользователя киоска:
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

function Find-Python {
    $candidates = @(
        (Get-Command py -ErrorAction SilentlyContinue),
        (Get-Command python -ErrorAction SilentlyContinue)
    ) | Where-Object { $_ }
    foreach ($cmd in $candidates) {
        if ($cmd.Name -eq "py") {
            $ver = & py -3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
            if ($ver -and ([version]$ver -ge [version]"3.11")) {
                return @{ Exe = "py"; Args = @("-3") }
            }
        } else {
            $ver = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
            if ($ver -and ([version]$ver -ge [version]"3.11")) {
                return @{ Exe = "python"; Args = @() }
            }
        }
    }
    return $null
}

Write-Host "=== Установка киоска ===" -ForegroundColor Cyan
Write-Host "Папка: $Root"

$py = Find-Python
if (-not $py) {
    Write-Host "ОШИБКА: нужен Python 3.11+ (https://www.python.org/downloads/windows/)" -ForegroundColor Red
    Write-Host "При установке отметьте «Add python.exe to PATH»."
    exit 1
}
Write-Host "Python: $($py.Exe) $($py.Args -join ' ')"

# Конфиг (не перезаписываем существующие)
$settingsExample = Join-Path $Root "config\settings.yaml.example"
$settings = Join-Path $Root "config\settings.yaml"
if (-not (Test-Path $settings)) {
    Copy-Item $settingsExample $settings
    Write-Host "Создан config\settings.yaml из примера."
} else {
    Write-Host "config\settings.yaml уже есть — не трогаем."
}

$envExample = Join-Path $Root ".env.example"
$envFile = Join-Path $Root ".env"
if (-not (Test-Path $envFile)) {
    Copy-Item $envExample $envFile
    Write-Host "Создан .env из примера — заполните ключи API."
} else {
    Write-Host ".env уже есть — не трогаем."
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
        Write-Host "Пресет mode_$Preset.yaml — вручную перенесите секции в config\settings.yaml" -ForegroundColor Yellow
        Write-Host "  См. docs\INSTALL_TERMINAL_WIN10.md, раздел «Пресеты режима оплаты»."
    }
}

# venv
$venv = Join-Path $Root ".venv"
$venvPy = Join-Path $venv "Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    Write-Host "Создаём виртуальное окружение..."
    & $py.Exe @($py.Args + @("-m", "venv", $venv))
}
Write-Host "Устанавливаем зависимости (pip)..."
& $venvPy -m pip install --upgrade pip --quiet
& $venvPy -m pip install -r (Join-Path $Root "requirements.txt")

Write-Host "Проверка импорта PyQt6..."
& $venvPy -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"

if ($Autostart) {
    & (Join-Path $Root "install_autostart.ps1")
}

Write-Host ""
Write-Host "=== Готово ===" -ForegroundColor Green
Write-Host "1. Отредактируйте config\settings.yaml и .env (ключи CRM, оплата)."
Write-Host "2. Запуск: run_kiosk.bat  или  run_kiosk_silent.bat (без консоли)."
Write-Host "3. Полная инструкция: docs\INSTALL_TERMINAL_WIN10.md"
if (-not $Autostart) {
    Write-Host "4. Автозапуск: .\install.ps1 -Autostart"
}
