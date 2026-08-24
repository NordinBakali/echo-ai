$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$batchLauncherPath = Join-Path $projectRoot 'Start-Echo-App.bat'
$vbsLauncherPath = Join-Path $projectRoot 'Echo-App.vbs'
$liveSyncBatchLauncherPath = Join-Path $projectRoot 'Start-Echo-App-LiveSync.bat'
$liveSyncVbsLauncherPath = Join-Path $projectRoot 'Echo-App-LiveSync.vbs'
$desktopPath = [Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path $desktopPath 'Echo App.lnk'
$liveSyncShortcutPath = Join-Path $desktopPath 'Echo App (Live Sync).lnk'

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

Write-Host "Desktop shortcut created: $shortcutPath"
Write-Host "Shortcut target: $launcherPath"
Write-Host "Desktop shortcut created: $liveSyncShortcutPath"
Write-Host "Shortcut target: $liveSyncLauncherPath"
