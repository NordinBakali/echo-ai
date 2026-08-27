$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$batchLauncherPath = Join-Path $projectRoot 'Start-Echo-App.bat'
$vbsLauncherPath = Join-Path $projectRoot 'Echo-App.vbs'
$liveSyncBatchLauncherPath = Join-Path $projectRoot 'Start-Echo-App-LiveSync.bat'
$liveSyncVbsLauncherPath = Join-Path $projectRoot 'Echo-App-LiveSync.vbs'
$autoSyncBatchLauncherPath = Join-Path $projectRoot 'Start-Echo-App-AutoSync.bat'
$autoSyncVbsLauncherPath = Join-Path $projectRoot 'Echo-App-AutoSync.vbs'
$wakeBatchLauncherPath = Join-Path $projectRoot 'Start-Echo-WakeListener.bat'
$wakeVbsLauncherPath = Join-Path $projectRoot 'Echo-Wake-Listener.vbs'
$desktopPath = [Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path $desktopPath 'Echo App.lnk'
$liveSyncShortcutPath = Join-Path $desktopPath 'Echo App (Live Sync).lnk'
$autoSyncShortcutPath = Join-Path $desktopPath 'Echo App (Auto Sync).lnk'
$wakeShortcutPath = Join-Path $desktopPath 'Echo Wake Listener.lnk'

function Resolve-LauncherPath {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Candidates,
        [Parameter(Mandatory = $true)]
        [string]$ErrorLabel
    )

    foreach ($candidate in $Candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    throw "Launcher not found for $ErrorLabel. Expected one of: $($Candidates -join ', ')"
}

$launcherPath = Resolve-LauncherPath -Candidates @($vbsLauncherPath, $batchLauncherPath) -ErrorLabel 'default launcher'
$liveSyncLauncherPath = Resolve-LauncherPath -Candidates @($liveSyncVbsLauncherPath, $liveSyncBatchLauncherPath) -ErrorLabel 'live sync launcher'
$autoSyncLauncherPath = Resolve-LauncherPath -Candidates @($autoSyncVbsLauncherPath, $autoSyncBatchLauncherPath) -ErrorLabel 'auto sync launcher'
$wakeLauncherPath = Resolve-LauncherPath -Candidates @($wakeVbsLauncherPath, $wakeBatchLauncherPath) -ErrorLabel 'wake listener launcher'

$wshShell = New-Object -ComObject WScript.Shell
$shortcut = $wshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $launcherPath
$shortcut.WorkingDirectory = $projectRoot
$shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,220"
$shortcut.Description = 'Start Echo as a desktop app'
$shortcut.Save()

$liveSyncShortcut = $wshShell.CreateShortcut($liveSyncShortcutPath)
$liveSyncShortcut.TargetPath = $liveSyncLauncherPath
$liveSyncShortcut.WorkingDirectory = $projectRoot
$liveSyncShortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,220"
$liveSyncShortcut.Description = 'Start Echo with live source sync'
$liveSyncShortcut.Save()

$autoSyncShortcut = $wshShell.CreateShortcut($autoSyncShortcutPath)
$autoSyncShortcut.TargetPath = $autoSyncLauncherPath
$autoSyncShortcut.WorkingDirectory = $projectRoot
$autoSyncShortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,220"
$autoSyncShortcut.Description = 'Start Echo with automatic source sync'
$autoSyncShortcut.Save()

$wakeShortcut = $wshShell.CreateShortcut($wakeShortcutPath)
$wakeShortcut.TargetPath = $wakeLauncherPath
$wakeShortcut.WorkingDirectory = $projectRoot
$wakeShortcut.IconLocation = "$env:SystemRoot\System32\SndVolSSO.dll,0"
$wakeShortcut.Description = 'Start the Echo wake listener (say hey echo to open the app when closed)'
$wakeShortcut.Save()

Write-Host "Desktop shortcut created: $shortcutPath"
Write-Host "Shortcut target: $launcherPath"
Write-Host "Desktop shortcut created: $liveSyncShortcutPath"
Write-Host "Shortcut target: $liveSyncLauncherPath"
Write-Host "Desktop shortcut created: $autoSyncShortcutPath"
Write-Host "Shortcut target: $autoSyncLauncherPath"
Write-Host "Desktop shortcut created: $wakeShortcutPath"
Write-Host "Shortcut target: $wakeLauncherPath"
