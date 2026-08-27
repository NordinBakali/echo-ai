@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [Echo] Creating virtual environment for wake listener...
    where py >nul 2>nul
    if %errorlevel%==0 (
        py -3 -m venv .venv
    ) else (
        python -m venv .venv
    )
)

if not exist ".venv\Scripts\python.exe" (
    echo [Echo] Python virtual environment could not be created.
    exit /b 1
)

set "PYTHON_EXE=.venv\Scripts\python.exe"

"%PYTHON_EXE%" -c "import speech_recognition" >nul 2>nul
if errorlevel 1 (
    echo [Echo] Installing wake listener dependencies...
    "%PYTHON_EXE%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [Echo] Dependency installation failed for wake listener.
        exit /b 1
    )
)

echo [Echo] Starting wake listener...
"%PYTHON_EXE%" echo_wake_listener.py

endlocal
