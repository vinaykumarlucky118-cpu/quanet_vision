@echo off
title QuaNet Vision Server
echo ========================================================
echo   Starting QuaNet Vision Web Server...
echo ========================================================
cd /d "%~dp0"

IF EXIST "C:\Users\vinay\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe" (
    set "PYTHON_EXE=C:\Users\vinay\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe"
) ELSE IF EXIST ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) ELSE (
    set "PYTHON_EXE=python"
)

echo Using Python: %PYTHON_EXE%
echo Starting server at http://127.0.0.1:5000 ...
"%PYTHON_EXE%" app.py
pause
