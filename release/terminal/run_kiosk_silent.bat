@echo off
REM Запуск без консоли (для ручного старта или отладки pythonw).
cd /d "%~dp0"
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" "main.py"
) else (
    start "" pyw -3 "main.py"
)
