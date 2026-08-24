ECHO APP (PORTABLE)
===================

1) Double-click Echo-App.vbs (or Start-Echo-App.bat)
  For live source mirroring during development, use Echo-App-LiveSync.vbs
2) Echo opens automatically in app window mode
3) Optional: run Install-Echo-Desktop-Shortcut.ps1 to put Echo on desktop

GITHUB SYNC
===========

- One-time/manual sync:
  Sync-GitHub.bat -RepoUrl https://github.com/<user>/<repo>.git

- Automatic watch sync:
  powershell -ExecutionPolicy Bypass -File .\Sync-GitHub.ps1 -RepoUrl https://github.com/<user>/<repo>.git -Watch

NOTES
=====

- The launcher enables auto-reload and auto-open during development.
- Echo-App.vbs runs the launcher without showing a terminal window.
- Echo-App-LiveSync.vbs starts Echo and enables continuous sync to release/Echo-App.
- If Git is not installed, install it first: https://git-scm.com/download/win
