[CmdletBinding()]
param(
    [switch]$Scan,
    [string]$Open,
    [switch]$Json
)

$ErrorActionPreference = 'Stop'

function Get-AppSearchFolders {
    @(
        (Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs'),
        (Join-Path $env:ProgramData 'Microsoft\Windows\Start Menu\Programs'),
        (Join-Path ([Environment]::GetFolderPath('Desktop')) ''),
        (Join-Path $env:PUBLIC 'Desktop')
    ) | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -Unique
}

function Get-DiscoveredApps {
    $excludedWords = @('uninstall', 'readme', 'help', 'documentation')
    $apps = @{}

    foreach ($folder in Get-AppSearchFolders) {
        Get-ChildItem -LiteralPath $folder -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Extension -in @('.lnk', '.url', '.exe') } |
            ForEach-Object {
                $name = $_.BaseName -replace '[^a-zA-Z0-9 ._-]', ' '
                $name = ($name -replace '\s+', ' ').Trim(' ', '.', '_', '-')
                if (-not $name) { return }
                if ($excludedWords | Where-Object { $name -match [regex]::Escape($_) }) { return }

                $key = $name.ToLowerInvariant()
                if (-not $apps.ContainsKey($key)) {
                    $apps[$key] = [PSCustomObject]@{
                        Name = $name
                        Path = $_.FullName
                        Type = $_.Extension.ToLowerInvariant()
                    }
                }
            }
    }

    @($apps.Values | Sort-Object Name)
}

function Find-AppMatch {
    param([Parameter(Mandatory)][string]$Name)

    $normalizedName = ($Name -replace '[^a-zA-Z0-9 ._-]', ' ' -replace '\s+', ' ').Trim()
    $apps = @(Get-DiscoveredApps)
    $exact = @($apps | Where-Object { $_.Name -ieq $normalizedName })
    if ($exact.Count -eq 1) { return $exact[0] }

    $partial = @($apps | Where-Object {
        $_.Name.IndexOf($normalizedName, [StringComparison]::OrdinalIgnoreCase) -ge 0
    })
    if ($partial.Count -eq 1) { return $partial[0] }
    if ($partial.Count -gt 1) {
        throw "Meerdere apps gevonden voor '$Name': $($partial.Name -join ', ')"
    }

    throw "App '$Name' niet gevonden in het Startmenu of op het bureaublad."
}

if (-not $Scan -and [string]::IsNullOrWhiteSpace($Open)) {
    Write-Host 'Gebruik:'
    Write-Host '  .\Echo-App-Scanner.ps1 -Scan'
    Write-Host '  .\Echo-App-Scanner.ps1 -Open "Spotify"'
    exit 1
}

if ($Scan) {
    $result = @(Get-DiscoveredApps)
    if ($Json) {
        $result | ConvertTo-Json -Depth 2
    } else {
        Write-Host "Gevonden apps: $($result.Count)"
        $result | ForEach-Object { Write-Host "- $($_.Name) [$($_.Type)]" }
    }
}

if (-not [string]::IsNullOrWhiteSpace($Open)) {
    $app = Find-AppMatch -Name $Open
    Start-Process -FilePath $app.Path
    Write-Host "Gestart: $($app.Name)"
}
