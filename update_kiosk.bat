@echo off
setlocal EnableExtensions

rem Obnovlenie kiosk s GitHub -> C:\kiosk (iz repozitoriya razrabotki)
set "TARGET=C:\kiosk"
if not "%~1"=="" set "TARGET=%~1"

cd /d "%~dp0"

echo.
echo Obnovlenie kiosk iz GitHub v %TARGET%
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\update_kiosk_from_git.ps1" -Target "%TARGET%"
set "ERR=%ERRORLEVEL%"

if not "%ERR%"=="0" (
    echo Oshibka: %ERR%
    pause
    exit /b %ERR%
)

pause
endlocal
