[CmdletBinding()]
param(
    [switch]$Scan,
    [string]$Open,
    [switch]$Json,
    [string]$WebsiteCheck,
    [string]$WebsiteCheckOutput,
    [switch]$WebsiteCheckVisual,
    [string]$WebsiteCheckVisualOutput
)

$ErrorActionPreference = 'Stop'

function Show-Usage {
    Write-Host 'Gebruik:'
    Write-Host '  .\Echo-App-Scanner.ps1 -Scan [-Json]'
    Write-Host '  .\Echo-App-Scanner.ps1 -Open "Spotify"'
    Write-Host '  .\Echo-App-Scanner.ps1 -WebsiteCheck "https://example.com" [-Json] [-WebsiteCheckOutput "report.json"] [-WebsiteCheckVisual] [-WebsiteCheckVisualOutput "report.html"]'
}

function Resolve-PythonLauncher {
    if (Get-Command -Name py -ErrorAction SilentlyContinue) {
        return @('py', '-3')
    }

    if (Get-Command -Name python -ErrorAction SilentlyContinue) {
        return @('python')
    }

    throw 'Geen Python runtime gevonden. Installeer Python 3 of gebruik py launcher.'
}

function Invoke-WebsiteFunctionalCheck {
    param(
        [Parameter(Mandatory)][string]$Url,
        [switch]$AsJson,
        [string]$OutputPath,
        [switch]$AsVisual,
        [string]$VisualOutputPath
    )

    $checkerPath = Join-Path $PSScriptRoot 'website_functional_check.py'
    if (-not (Test-Path -LiteralPath $checkerPath)) {
        throw "Website checker niet gevonden: $checkerPath"
    }

    $launcher = Resolve-PythonLauncher
    $pythonCommand = $launcher[0]
    $args = @()
    if ($launcher.Count -gt 1) {
        $args += $launcher[1..($launcher.Count - 1)]
    }

    $args += @($checkerPath, '--url', $Url)

    if ($AsJson) {
        $args += '--json'
    }

    if (-not [string]::IsNullOrWhiteSpace($OutputPath)) {
        $args += @('--output', $OutputPath)
    }

    if (-not [string]::IsNullOrWhiteSpace($VisualOutputPath)) {
        $args += @('--visual-output', $VisualOutputPath)
    }

    if ($AsVisual) {
        $args += '--open-visual'
    }

    & $pythonCommand @args
    if ($LASTEXITCODE -ne 0) {
        throw "Website checker faalde met exitcode $LASTEXITCODE."
    }
}

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

if (($Scan -and -not [string]::IsNullOrWhiteSpace($Open)) -or
    ($Scan -and -not [string]::IsNullOrWhiteSpace($WebsiteCheck)) -or
    (-not [string]::IsNullOrWhiteSpace($Open) -and -not [string]::IsNullOrWhiteSpace($WebsiteCheck))) {
    Write-Host 'Gebruik precies 1 hoofdactie per run.'
    Show-Usage
    exit 1
}

if (-not $Scan -and [string]::IsNullOrWhiteSpace($Open) -and [string]::IsNullOrWhiteSpace($WebsiteCheck)) {
    Show-Usage
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

if (-not [string]::IsNullOrWhiteSpace($WebsiteCheck)) {
    Invoke-WebsiteFunctionalCheck `
        -Url $WebsiteCheck `
        -AsJson:$Json `
        -OutputPath $WebsiteCheckOutput `
        -AsVisual:$WebsiteCheckVisual `
        -VisualOutputPath $WebsiteCheckVisualOutput
}
