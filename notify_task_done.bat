@echo off
setlocal

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "scripts\notify_task_done.py" %*
) else (
    py -3 "scripts\notify_task_done.py" %*
)

endlocal
