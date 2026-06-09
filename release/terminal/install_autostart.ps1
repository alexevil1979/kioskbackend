# Ярлык автозапуска киоска в shell:startup (без окна консоли).
$Root = $PSScriptRoot
$pythonw = Join-Path $Root ".venv\Scripts\pythonw.exe"
$main = Join-Path $Root "main.py"

if (-not (Test-Path $pythonw)) {
    Write-Host "ОШИБКА: сначала выполните install.ps1" -ForegroundColor Red
    exit 1
}

$startup = [Environment]::GetFolderPath("Startup")
$lnk = Join-Path $startup "SadyKolomnyKiosk.lnk"
$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($lnk)
$shortcut.TargetPath = $pythonw
$shortcut.Arguments = "`"$main`""
$shortcut.WorkingDirectory = $Root
$shortcut.WindowStyle = 7
$shortcut.Description = "Сады Коломны — киоск"
$shortcut.Save()
Write-Host "Автозапуск: $lnk" -ForegroundColor Green
