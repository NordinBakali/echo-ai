ECHO APP (PORTABLE)
===================

1) Double-click Start-Echo-App.bat
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
- If Git is not installed, install it first: https://git-scm.com/download/win
