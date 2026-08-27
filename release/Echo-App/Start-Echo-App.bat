@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

if exist "Sync-Echo-App.ps1" (
    echo [Echo] Syncing app package files...
    powershell -NoProfile -ExecutionPolicy Bypass -File ".\Sync-Echo-App.ps1" -Quiet
    if errorlevel 1 (
        echo [Echo] Warning: app package sync failed. Continuing startup...
    )
)

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

if not defined ECHO_PORT set "ECHO_PORT=5000"
if not defined ECHO_PORT_SPAN set "ECHO_PORT_SPAN=10"
if not defined ECHO_WINDOW_MODE set "ECHO_WINDOW_MODE=app"
if not defined ECHO_AUTO_OPEN set "ECHO_AUTO_OPEN=1"
if not defined ECHO_AUTO_RELOAD set "ECHO_AUTO_RELOAD=1"
if not defined ECHO_OPEN_ON_RELOAD set "ECHO_OPEN_ON_RELOAD=0"
if not defined ECHO_AUTOSTART_WAKE_LISTENER set "ECHO_AUTOSTART_WAKE_LISTENER=1"
if not defined ECHO_REOPEN_WHEN_RUNNING set "ECHO_REOPEN_WHEN_RUNNING=1"

if /I "%ECHO_AUTOSTART_WAKE_LISTENER%"=="1" (
    if exist "Echo-Wake-Listener.vbs" (
        start "" /b wscript.exe "%cd%\Echo-Wake-Listener.vbs"
    ) else if exist "Start-Echo-WakeListener.bat" (
        start "" /b "%cd%\Start-Echo-WakeListener.bat"
    )
)

if exist "echo_launch_helper.py" (
    set "LAUNCH_HELPER_ARGS=--preferred-port %ECHO_PORT% --port-span %ECHO_PORT_SPAN% --window-mode %ECHO_WINDOW_MODE%"
    if /I "%ECHO_REOPEN_WHEN_RUNNING%"=="1" set "LAUNCH_HELPER_ARGS=%LAUNCH_HELPER_ARGS% --reopen-if-running"

    "%PYTHON_EXE%" echo_launch_helper.py %LAUNCH_HELPER_ARGS%
    set "LAUNCH_PRECHECK_EXIT=!ERRORLEVEL!"

    if "!LAUNCH_PRECHECK_EXIT!"=="10" (
        if /I "%ECHO_REOPEN_WHEN_RUNNING%"=="1" (
            echo [Echo] Existing Echo instance detected. Reopened existing app window.
        ) else (
            echo [Echo] Existing Echo instance detected. Skipping duplicate startup.
        )
        endlocal
        exit /b 0
    )

    if not "!LAUNCH_PRECHECK_EXIT!"=="0" (
        echo [Echo] Launch pre-check returned !LAUNCH_PRECHECK_EXIT!. Continuing startup...
    )
)

echo [Echo] Starting Echo Flask app mode...
"%PYTHON_EXE%" server.py

endlocal
