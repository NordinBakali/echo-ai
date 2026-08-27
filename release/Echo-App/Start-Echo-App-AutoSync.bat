@echo off
setlocal
cd /d "%~dp0"

if exist "Start-Echo-App-LiveSync.bat" (
    call ".\Start-Echo-App-LiveSync.bat"
) else (
    echo [Echo] Start-Echo-App-LiveSync.bat not found.
    echo [Echo] Falling back to standard launcher...
    call ".\Start-Echo-App.bat"
)

endlocal
