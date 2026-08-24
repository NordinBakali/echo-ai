$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$releaseRoot = Join-Path $projectRoot 'release'
$packageRoot = Join-Path $releaseRoot 'Echo-App'
$zipPath = Join-Path $releaseRoot 'Echo-App-Portable.zip'

if (Test-Path $packageRoot) {
    Remove-Item -Path $packageRoot -Recurse -Force
}

if (-not (Test-Path $releaseRoot)) {
    New-Item -Path $releaseRoot -ItemType Directory | Out-Null
}

New-Item -Path $packageRoot -ItemType Directory | Out-Null

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
    'Start-Echo-App.bat',
    'Echo-App.vbs',
    'Install-Echo-Desktop-Shortcut.ps1',
    'Sync-GitHub.ps1',
    'Sync-GitHub.bat',
    'PORTABLE-APP-README.txt'
)

foreach ($item in $itemsToCopy) {
    $source = Join-Path $projectRoot $item
    if (Test-Path $source) {
        Copy-Item -Path $source -Destination $packageRoot -Recurse -Force
    }
}

if (Test-Path $zipPath) {
    Remove-Item -Path $zipPath -Force
}

Compress-Archive -Path (Join-Path $packageRoot '*') -DestinationPath $zipPath -Force

Write-Host "Portable package created: $zipPath"
