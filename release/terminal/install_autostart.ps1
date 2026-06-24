# Autostart shortcut in shell:startup (no console window).
$Root = $PSScriptRoot
$pythonw = Join-Path $Root ".venv\Scripts\pythonw.exe"
$main = Join-Path $Root "main.py"

if (-not (Test-Path $pythonw)) {
    Write-Host "ERROR: run install.ps1 first" -ForegroundColor Red
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
$shortcut.Description = "Sady Kolomny Kiosk"
$shortcut.Save()
Write-Host "Autostart: $lnk" -ForegroundColor Green
