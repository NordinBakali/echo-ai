$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$batchLauncherPath = Join-Path $projectRoot 'Start-Echo-App.bat'
$vbsLauncherPath = Join-Path $projectRoot 'Echo-App.vbs'
$desktopPath = [Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path $desktopPath 'Echo App.lnk'

if (Test-Path $vbsLauncherPath) {
    $launcherPath = $vbsLauncherPath
} elseif (Test-Path $batchLauncherPath) {
    $launcherPath = $batchLauncherPath
} else {
    throw "Launcher not found. Expected one of: $vbsLauncherPath or $batchLauncherPath"
}

$wshShell = New-Object -ComObject WScript.Shell
$shortcut = $wshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $launcherPath
$shortcut.WorkingDirectory = $projectRoot
$shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,220"
$shortcut.Description = 'Start Echo as a desktop app'
$shortcut.Save()

Write-Host "Desktop shortcut created: $shortcutPath"
Write-Host "Shortcut target: $launcherPath"
