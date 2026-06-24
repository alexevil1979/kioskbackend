# Remove kiosk autostart shortcut.
$startup = [Environment]::GetFolderPath("Startup")
foreach ($name in @("SadyKolomnyKiosk.lnk", "KioskFarm.lnk")) {
    $lnk = Join-Path $startup $name
    if (Test-Path $lnk) {
        Remove-Item $lnk -Force
        Write-Host "Removed: $lnk"
    }
}
Write-Host "Done."
