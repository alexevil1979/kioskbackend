@echo off
setlocal EnableExtensions

rem Obnovlenie kioska s GitHub (vetka main) -> C:\kiosk
rem Zapusk: update_kiosk.bat [put]

set "TARGET=C:\kiosk"
if not "%~1"=="" set "TARGET=%~1"

cd /d "%~dp0"

if exist "%~dp0update_kiosk.ps1" (
    set "PS1=%~dp0update_kiosk.ps1"
) else if exist "%~dp0scripts\update_kiosk_from_git.ps1" (
    set "PS1=%~dp0scripts\update_kiosk_from_git.ps1"
) else (
    echo OSHIBKA: ne nayden update_kiosk.ps1
    pause
    exit /b 1
)

echo.
echo Obnovlenie kioska iz GitHub v %TARGET%
echo Zakroyte okno kioska pered obnovleniem.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -Target "%TARGET%"
set "ERR=%ERRORLEVEL%"

if not "%ERR%"=="0" (
    echo.
    echo Obnovlenie zavershilos s oshibkoy: %ERR%
    pause
    exit /b %ERR%
)

echo.
echo Gotovo. Zapusk: %TARGET%\run_kiosk.bat
pause
endlocal
