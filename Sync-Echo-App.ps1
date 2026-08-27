param(
    [switch]$Watch,
    [switch]$Quiet,
    [switch]$SkipInitialSync
)

$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$releaseRoot = Join-Path $projectRoot 'release'
$packageRoot = Join-Path $releaseRoot 'Echo-App'
$watchLockPath = Join-Path $releaseRoot '.echo-sync-watch.lock'
$syncMutexName = 'Global\EchoSyncCopy_' + [Math]::Abs($projectRoot.ToLowerInvariant().GetHashCode())
$syncMutex = New-Object System.Threading.Mutex($false, $syncMutexName)

$itemsToCopy = @(
    'server.py',
    'ai_core.py',
    'README.md',
    'requirements.txt',
    'pytest.ini',
    'instellingen.json',
    '.env.example',
    '.gitignore',
    'static',
    'templates',
    'tests',
    'gemini-node',
    'Start-Echo-App.bat',
    'Start-Echo-App-LiveSync.bat',
    'Start-Echo-App-AutoSync.bat',
    'Start-Echo-WakeListener.bat',
    'Echo-App.vbs',
    'Echo-App-LiveSync.vbs',
    'Echo-App-AutoSync.vbs',
    'Echo-Wake-Listener.vbs',
    'echo_launch_helper.py',
    'echo_wake_listener.py',
    'Install-Echo-Desktop-Shortcut.ps1',
    'Set-OpenAI-Key.ps1',
    'Sync-GitHub.ps1',
    'Sync-GitHub.bat',
    'PORTABLE-APP-README.txt'
)

function Write-SyncMessage {
    param([string]$Message)

    if (-not $Quiet) {
        Write-Host $Message
    }
}

function Invoke-EchoAppSync {
    $hasSyncMutex = $false
    $stagingRoot = Join-Path $releaseRoot 'Echo-App.__staging'
    $backupRoot = Join-Path $releaseRoot 'Echo-App.__backup'

    try {
        $hasSyncMutex = $syncMutex.WaitOne([timespan]::FromSeconds(30))
        if (-not $hasSyncMutex) {
            throw 'Could not acquire sync lock within 30 seconds.'
        }

        if (-not (Test-Path $releaseRoot)) {
            New-Item -Path $releaseRoot -ItemType Directory -Force | Out-Null
        }

        if (Test-Path $stagingRoot) {
            Remove-Item -Path $stagingRoot -Recurse -Force -ErrorAction SilentlyContinue
        }

        if (Test-Path $backupRoot) {
            Remove-Item -Path $backupRoot -Recurse -Force -ErrorAction SilentlyContinue
        }

        New-Item -Path $stagingRoot -ItemType Directory -Force | Out-Null

        $copiedItems = 0

        foreach ($item in $itemsToCopy) {
            $source = Join-Path $projectRoot $item
            if (Test-Path $source) {
                Copy-Item -Path $source -Destination $stagingRoot -Recurse -Force
                $copiedItems++
            }
            else {
                Write-SyncMessage "Skipping missing source item: $item"
            }
        }

        if ($copiedItems -eq 0) {
            throw 'Sync aborted: no source items were copied into the staging package.'
        }

        if (Test-Path $packageRoot) {
            Move-Item -Path $packageRoot -Destination $backupRoot -Force
        }

        Move-Item -Path $stagingRoot -Destination $packageRoot -Force

        if (Test-Path $backupRoot) {
            Remove-Item -Path $backupRoot -Recurse -Force -ErrorAction SilentlyContinue
        }

        Write-SyncMessage "Echo app synced to: $packageRoot"
    }
    catch {
        if (Test-Path $stagingRoot) {
            Remove-Item -Path $stagingRoot -Recurse -Force -ErrorAction SilentlyContinue
        }

        if (-not (Test-Path $packageRoot) -and (Test-Path $backupRoot)) {
            Move-Item -Path $backupRoot -Destination $packageRoot -Force
        }

        throw
    }
    finally {
        if ($hasSyncMutex) {
            $syncMutex.ReleaseMutex()
        }
    }
}

function Acquire-WatchLock {
    if (-not (Test-Path $releaseRoot)) {
        New-Item -Path $releaseRoot -ItemType Directory | Out-Null
    }

    try {
        return [System.IO.File]::Open(
            $watchLockPath,
            [System.IO.FileMode]::OpenOrCreate,
            [System.IO.FileAccess]::ReadWrite,
            [System.IO.FileShare]::None
        )
    }
    catch {
        return $null
    }
}

function Should-SkipPath {
    param([string]$FullPath)

    if ([string]::IsNullOrWhiteSpace($FullPath)) {
        return $true
    }

    $normalized = $FullPath.ToLowerInvariant()

    if ($normalized.Contains('\release\')) { return $true }
    if ($normalized.Contains('\.venv\')) { return $true }
    if ($normalized.Contains('\__pycache__\')) { return $true }
    if ($normalized.Contains('\node_modules\')) { return $true }
    if ($normalized.EndsWith('.pyc')) { return $true }

    return $false
}

if (-not $SkipInitialSync) {
    Invoke-EchoAppSync
}

if (-not $Watch) {
    return
}

$watchLockHandle = Acquire-WatchLock
if (-not $watchLockHandle) {
    Write-SyncMessage 'Watch sync is already running for this workspace.'
    return
}

Write-SyncMessage 'Watch mode enabled. Waiting for source changes...'

$watcher = New-Object System.IO.FileSystemWatcher $projectRoot, '*'
$watcher.IncludeSubdirectories = $true
$watcher.NotifyFilter = [System.IO.NotifyFilters]'FileName, DirectoryName, LastWrite, CreationTime, Size'
$lastSyncAt = [datetime]::UtcNow

try {
    while ($true) {
        $change = $watcher.WaitForChanged([System.IO.WatcherChangeTypes]::All, 2000)
        if ($change.TimedOut) {
            continue
        }

        $changedPath = if ([string]::IsNullOrWhiteSpace($change.Name)) {
            $projectRoot
        } else {
            Join-Path $projectRoot $change.Name
        }

        if (Should-SkipPath -FullPath $changedPath) {
            continue
        }

        $now = [datetime]::UtcNow
        if (($now - $lastSyncAt) -lt [timespan]::FromMilliseconds(750)) {
            continue
        }

        Invoke-EchoAppSync
        $lastSyncAt = $now
    }
}
finally {
    $watcher.Dispose()
    if ($watchLockHandle) {
        $watchLockHandle.Dispose()
        Remove-Item -Path $watchLockPath -Force -ErrorAction SilentlyContinue
    }
}
