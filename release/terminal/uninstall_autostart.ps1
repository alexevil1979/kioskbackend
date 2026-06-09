# Удалить ярлык автозапуска киоска.
$startup = [Environment]::GetFolderPath("Startup")
foreach ($name in @("SadyKolomnyKiosk.lnk", "KioskFarm.lnk")) {
    $lnk = Join-Path $startup $name
    if (Test-Path $lnk) {
        Remove-Item $lnk -Force
        Write-Host "Удалён: $lnk"
    }
}
Write-Host "Готово."
