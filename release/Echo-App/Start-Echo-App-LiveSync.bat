@echo off
setlocal
cd /d "%~dp0"

if exist "Sync-Echo-App.ps1" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath powershell -WindowStyle Hidden -WorkingDirectory '%~dp0' -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File','%~dp0Sync-Echo-App.ps1','-Watch','-Quiet','-SkipInitialSync')" >nul 2>nul
)

call ".\Start-Echo-App.bat"

endlocal
