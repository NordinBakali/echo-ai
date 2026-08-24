@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [Echo] Creating virtual environment...
    where py >nul 2>nul
    if %errorlevel%==0 (
        py -3 -m venv .venv
    ) else (
        python -m venv .venv
    )
)

if not exist ".venv\Scripts\python.exe" (
    echo [Echo] Python virtual environment could not be created.
    echo [Echo] Install Python 3.10+ and try again.
    pause
    exit /b 1
)

set "PYTHON_EXE=.venv\Scripts\python.exe"

echo [Echo] Installing dependencies...
"%PYTHON_EXE%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [Echo] Dependency installation failed.
    pause
    exit /b 1
)

set "ECHO_WINDOW_MODE=app"
set "ECHO_AUTO_OPEN=1"
set "ECHO_AUTO_RELOAD=1"
set "ECHO_OPEN_ON_RELOAD=1"

echo [Echo] Starting Echo app mode...
"%PYTHON_EXE%" server.py

endlocal
