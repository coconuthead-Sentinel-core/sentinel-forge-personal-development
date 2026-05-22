# Sentinel Forge -> Obsidian setup
# Registers the Books folder as an Obsidian vault and drops a starter
# README so opening the vault for the first time is a one-click experience.
#
#   powershell -ExecutionPolicy Bypass -File setup-obsidian.ps1

param(
    [string]$BooksPath = "$env:USERPROFILE\OneDrive\Desktop\Books"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $BooksPath)) {
    New-Item -ItemType Directory -Path $BooksPath -Force | Out-Null
    Write-Output "Created Books folder: $BooksPath"
}

# --- Register as an Obsidian vault ----------------------------------------
$obsConfigDir = "$env:APPDATA\Obsidian"
$obsConfigFile = Join-Path $obsConfigDir "obsidian.json"

if (-not (Test-Path $obsConfigDir)) {
    New-Item -ItemType Directory -Path $obsConfigDir -Force | Out-Null
}

$config = @{ vaults = @{} }
if (Test-Path $obsConfigFile) {
    try {
        $existing = Get-Content $obsConfigFile -Raw | ConvertFrom-Json
        if ($existing.vaults) {
            foreach ($p in $existing.vaults.PSObject.Properties) {
                $config.vaults[$p.Name] = $p.Value
            }
        }
    } catch {
        Write-Warning "Existing obsidian.json wasn't valid JSON - overwriting."
    }
}

$alreadyRegistered = $false
foreach ($id in $config.vaults.Keys) {
    $v = $config.vaults[$id]
    if ($v.path -and ($v.path -ieq $BooksPath)) { $alreadyRegistered = $true; break }
}

if (-not $alreadyRegistered) {
    $vaultId = -join ((48..57 + 97..102) | Get-Random -Count 16 | ForEach-Object { [char]$_ })
    $config.vaults[$vaultId] = @{
        path = $BooksPath
        ts   = [int64]((Get-Date).ToFileTimeUtc())
        open = $false
    }
    $config | ConvertTo-Json -Depth 6 | Set-Content -Path $obsConfigFile -Encoding UTF8
    Write-Output "Registered Obsidian vault: $BooksPath"
} else {
    Write-Output "Vault already registered: $BooksPath"
}

# --- Drop the starter README ----------------------------------------------
$readmeTarget = Join-Path $BooksPath "_Sentinel_Forge_Library.md"
$readmeSource = Join-Path $PSScriptRoot "sentinel-library-readme.md"
if (-not (Test-Path $readmeTarget)) {
    if (Test-Path $readmeSource) {
        Copy-Item $readmeSource $readmeTarget
        Write-Output "Wrote README: $readmeTarget"
    } else {
        Write-Warning "Source README not found at $readmeSource"
    }
} else {
    Write-Output "README already exists: $readmeTarget"
}

# --- .obsidian config for sensible defaults -------------------------------
$dotObsidian = Join-Path $BooksPath ".obsidian"
if (-not (Test-Path $dotObsidian)) {
    New-Item -ItemType Directory -Path $dotObsidian -Force | Out-Null
}

$appearance = Join-Path $dotObsidian "app.json"
if (-not (Test-Path $appearance)) {
    @{
        showLineNumber       = $true
        readableLineLength   = $true
        attachmentFolderPath = "."
    } | ConvertTo-Json | Set-Content -Path $appearance -Encoding UTF8
    Write-Output "Wrote .obsidian/app.json"
}

Write-Output ""
Write-Output "DONE. Next steps:"
Write-Output "  1. Launch Obsidian. The vault should appear in the Vault Switcher; pick 'Sentinel Forge Library'."
Write-Output "  2. Settings -> Community plugins -> Turn on community plugins -> Browse -> Dataview -> Install + Enable."
Write-Output "  3. Open _Sentinel_Forge_Library.md to see live Dataview queries over your saves."
