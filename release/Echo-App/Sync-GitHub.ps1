param(
    [string]$RepoUrl = '',
    [string]$Branch = 'main',
    [switch]$Watch,
    [int]$DebounceSeconds = 8
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Set-Location $PSScriptRoot

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host '[GitHub] Git is not installed or not in PATH.'
    Write-Host '[GitHub] Install Git first: https://git-scm.com/download/win'
    exit 1
}

function Ensure-Repository {
    if (-not (Test-Path '.git')) {
        Write-Host '[GitHub] Initializing local git repository...'
        git init | Out-Host
        git branch -M $Branch | Out-Host
    }
}

function Ensure-Remote {
    param([string]$Url)

    if (-not $Url) {
        return
    }

    $hasOrigin = $false
    try {
        $null = git remote get-url origin 2>$null
        if ($LASTEXITCODE -eq 0) {
            $hasOrigin = $true
        }
    } catch {
        $hasOrigin = $false
    }

    if ($hasOrigin) {
        Write-Host "[GitHub] Updating origin remote to $Url"
        git remote set-url origin $Url | Out-Host
    } else {
        Write-Host "[GitHub] Adding origin remote: $Url"
        git remote add origin $Url | Out-Host
    }
}

function Ensure-RemoteOrCreate {
    if ($RepoUrl) {
        Ensure-Remote -Url $RepoUrl
        return
    }

    try {
        $null = git remote get-url origin 2>$null
        if ($LASTEXITCODE -eq 0) {
            return
        }
    } catch {
        # Continue and create/provide remote.
    }

    if (Get-Command gh -ErrorAction SilentlyContinue) {
        $repoName = Split-Path -Path $PSScriptRoot -Leaf
        Write-Host "[GitHub] No origin found. Creating GitHub repo with gh: $repoName"
        gh repo create $repoName --source . --remote origin --private --push | Out-Host
        if ($LASTEXITCODE -ne 0) {
            throw '[GitHub] gh repo create failed. Run again with -RepoUrl.'
        }
        return
    }

    throw '[GitHub] No origin remote found. Run with -RepoUrl https://github.com/<user>/<repo>.git'
}

function Invoke-Sync {
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

    git add -A | Out-Null
    git diff --cached --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[GitHub] No new changes to sync at $timestamp"
        return
    }

    git commit -m "Auto sync $timestamp" | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw '[GitHub] Commit failed.'
    }

    $originUrl = git remote get-url origin 2>$null
    if (-not $originUrl) {
        throw '[GitHub] Origin remote is missing.'
    }

    git push -u origin $Branch | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw '[GitHub] Push failed. Check auth and branch permissions.'
    }

    Write-Host "[GitHub] Sync complete at $timestamp"
}

Ensure-Repository
Ensure-RemoteOrCreate
Invoke-Sync

if (-not $Watch) {
    exit 0
}

if ($DebounceSeconds -lt 2) {
    $DebounceSeconds = 2
}

Write-Host "[GitHub] Watch mode enabled. Auto-sync every change burst (${DebounceSeconds}s debounce)."

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $PSScriptRoot
$watcher.Filter = '*'
$watcher.IncludeSubdirectories = $true
$watcher.NotifyFilter = [System.IO.NotifyFilters]'FileName, LastWrite, DirectoryName, Size, CreationTime'
$watcher.EnableRaisingEvents = $true

$script:syncPending = $false

$onChange = {
    $fullPath = $Event.SourceEventArgs.FullPath
    if ($fullPath -match '\\.git\\' -or $fullPath -match '\\.venv\\' -or $fullPath -match '\\__pycache__\\') {
        return
    }
    $script:syncPending = $true
}

Register-ObjectEvent -InputObject $watcher -EventName Changed -Action $onChange | Out-Null
Register-ObjectEvent -InputObject $watcher -EventName Created -Action $onChange | Out-Null
Register-ObjectEvent -InputObject $watcher -EventName Deleted -Action $onChange | Out-Null
Register-ObjectEvent -InputObject $watcher -EventName Renamed -Action $onChange | Out-Null

while ($true) {
    $evt = Wait-Event -Timeout $DebounceSeconds
    if ($evt) {
        Remove-Event -EventIdentifier $evt.EventIdentifier | Out-Null
    }

    if (-not $script:syncPending) {
        continue
    }

    $script:syncPending = $false
    try {
        Invoke-Sync
    } catch {
        Write-Host $_.Exception.Message
    }
}
