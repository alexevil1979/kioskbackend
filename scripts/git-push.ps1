# Безопасный push в kioskbackend (без секретов)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

$blocked = @(
    "config/settings.yaml",
    ".env"
)
foreach ($b in $blocked) {
    if (git status --porcelain $b 2>$null) {
        $st = git status --porcelain $b
        if ($st -match "^[AM]") {
            Write-Error "В индексе чувствительный файл: $b — уберите из commit"
        }
    }
}

git add -A
$names = git diff --cached --name-only
foreach ($n in $names) {
    if ($n -match "settings\.yaml$" -and $n -notmatch "\.example") {
        Write-Error "Отмена: в commit попал $n"
    }
    if ($n -eq ".env") { Write-Error "Отмена: в commit попал .env" }
}

if (-not $names) {
    Write-Host "Нет изменений для commit"
    exit 0
}

$msg = $args[0]
if (-not $msg) { $msg = "Update kiosk project" }

git commit -m $msg
git push origin HEAD
Write-Host "OK: pushed to origin"
