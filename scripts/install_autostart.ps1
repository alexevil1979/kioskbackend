# Ярлык автозапуска киоска (запуск от имени администратора не обязателен)
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$python = Join-Path $projectRoot ".venv\Scripts\pythonw.exe"
$main = Join-Path $projectRoot "main.py"
$startup = [Environment]::GetFolderPath("Startup")
$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut((Join-Path $startup "KioskFarm.lnk"))
$shortcut.TargetPath = $python
$shortcut.Arguments = "`"$main`""
$shortcut.WorkingDirectory = $projectRoot
$shortcut.Save()
Write-Host "Автозапуск создан: $($shortcut.FullName)"
