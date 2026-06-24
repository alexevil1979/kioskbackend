@echo off
setlocal EnableExtensions

rem Skachat arhiv main s GitHub i raspakovat v papku kiosk (perezapis fajlov iz arhiva)
rem Po umolchaniyu: papka, gde lezhit etot batnik
rem   pull_kiosk_from_git.bat
rem   pull_kiosk_from_git.bat C:\kiosk

set "TARGET=%~dp0"
if "%TARGET:~-1%"=="\" set "TARGET=%TARGET:~0,-1%"
if not "%~1"=="" set "TARGET=%~1"

cd /d "%~dp0"

echo.
echo Skachivanie kioska s GitHub v %TARGET%
echo Fajly iz arhiva perezapishut sushhestvuyushhie.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\pull_kiosk_from_git.ps1" -Target "%TARGET%"
set "ERR=%ERRORLEVEL%"

if not "%ERR%"=="0" (
    echo.
    echo Oshibka: %ERR%
    pause
    exit /b %ERR%
)

echo.
pause
endlocal
