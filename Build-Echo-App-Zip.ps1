$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$releaseRoot = Join-Path $projectRoot 'release'
$packageRoot = Join-Path $releaseRoot 'Echo-App'
$zipPath = Join-Path $releaseRoot 'Echo-App-Portable.zip'
$syncScriptPath = Join-Path $projectRoot 'Sync-Echo-App.ps1'

if (-not (Test-Path $syncScriptPath)) {
    throw "Sync script not found: $syncScriptPath"
}

& $syncScriptPath -Quiet

if (Test-Path $zipPath) {
    Remove-Item -Path $zipPath -Force
}

Compress-Archive -Path (Join-Path $packageRoot '*') -DestinationPath $zipPath -Force

Write-Host "Portable package created: $zipPath"
