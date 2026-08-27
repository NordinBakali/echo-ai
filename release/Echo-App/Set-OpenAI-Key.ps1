param(
    [string]$Model = 'gpt-4.1-mini',
    [string]$BaseUrl = 'https://api.openai.com/v1'
)

$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$envPath = Join-Path $projectRoot '.env'

$secureKey = Read-Host -Prompt 'Plak je nieuwe OpenAI API key' -AsSecureString
$pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)

try {
    $apiKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
}

if ([string]::IsNullOrWhiteSpace($apiKey)) {
    $apiKey = ''
}
else {
    $apiKey = $apiKey.Trim()
}
if (-not $apiKey) {
    throw 'Geen API key ontvangen. Afgebroken.'
}

$lines = @()
if (Test-Path $envPath) {
    $lines = Get-Content -Path $envPath -Encoding UTF8
}

if (-not $lines) {
    $lines = @()
}

$updates = [ordered]@{
    'OPENAI_API_KEY' = $apiKey
    'OPENAI_MODEL' = $Model
    'OPENAI_BASE_URL' = $BaseUrl
    'OPENAI_TIMEOUT_SECONDS' = '180'
}

foreach ($entry in $updates.GetEnumerator()) {
    $name = [string]$entry.Key
    $value = [string]$entry.Value
    $pattern = '^\s*' + [regex]::Escape($name) + '\s*='
    $updated = $false

    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match $pattern) {
            $lines[$i] = "$name=$value"
            $updated = $true
            break
        }
    }

    if (-not $updated) {
        $lines += "$name=$value"
    }
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllLines($envPath, $lines, $utf8NoBom)

Write-Host "OpenAI configuratie opgeslagen in: $envPath"
Write-Host 'Herstart daarna Echo om de nieuwe sleutel te gebruiken.'
