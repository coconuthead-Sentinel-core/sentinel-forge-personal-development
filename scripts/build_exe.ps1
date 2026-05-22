# build_exe.ps1 — produce a distributable Sentinel-Forge.exe
#
# Uses the existing PyInstaller spec at the repo root. One-folder build
# (not one-file) so cold-start is fast and the bundled Piper voice + the
# .onnx model don't get extracted to a temp dir on every launch. Ship the
# whole dist\Sentinel-Forge\ folder.
#
# Run from the repo root:
#   powershell -ExecutionPolicy Bypass -File scripts\build_exe.ps1
#
# Output:
#   dist\Sentinel-Forge\Sentinel-Forge.exe   (~6 MB launcher)
#   dist\Sentinel-Forge\_internal\          (Python + bundled libs)
#   Total folder size: ~30 MB without TTS, ~175 MB with the Piper voice
#
# Notes:
#   - The spec auto-includes everything in ./tts if that folder exists.
#     Run scripts\install_tts.ps1 first if you want the .exe to include
#     the neural voice; otherwise the .exe still works with SAPI5.
#   - First-time PyInstaller install takes a few minutes. After that the
#     incremental rebuild is ~30 seconds.

param(
    [switch]$NoTTS,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path "$PSScriptRoot\.."
Set-Location $repoRoot

# 1. Make sure pyinstaller is available
$py = (Get-Command py -ErrorAction SilentlyContinue)
if (-not $py) { throw "Python launcher 'py' not found. Install Python 3.11+." }

Write-Host "Ensuring pyinstaller is installed..." -ForegroundColor Cyan
py -3 -m pip install --quiet --disable-pip-version-check pyinstaller

# 2. Optionally hide the tts/ folder so the spec doesn't bundle it
$ttsBackup = $null
if ($NoTTS -and (Test-Path "tts")) {
    $ttsBackup = Join-Path $env:TEMP "sentinel-forge-tts-tmp"
    if (Test-Path $ttsBackup) { Remove-Item $ttsBackup -Recurse -Force }
    Move-Item "tts" $ttsBackup
    Write-Host "tts/ temporarily moved out — build will be lean (~30 MB)." -ForegroundColor Yellow
}

try {
    # 3. Build
    $args = @("Sentinel-Forge.spec", "--noconfirm")
    if ($Clean) { $args += "--clean" }
    Write-Host "Running pyinstaller $($args -join ' ')..." -ForegroundColor Cyan
    py -3 -m PyInstaller @args

    # 4. Report
    $exe = "dist\Sentinel-Forge\Sentinel-Forge.exe"
    if (-not (Test-Path $exe)) {
        throw "Build appeared to succeed but $exe is missing."
    }
    $info     = Get-Item $exe
    $bundleMB = [math]::Round((Get-ChildItem "dist\Sentinel-Forge" -Recurse -File | Measure-Object Length -Sum).Sum / 1MB, 1)

    Write-Host ""
    Write-Host "Build complete." -ForegroundColor Green
    Write-Host "  EXE:    $($info.FullName)"
    Write-Host "  Size:   $([math]::Round($info.Length/1MB,2)) MB (launcher) · $bundleMB MB (whole folder)"
    Write-Host "  Ship:   the entire dist\Sentinel-Forge\ folder"
    Write-Host ""
    Write-Host "Smoke-test it:"
    Write-Host "  start dist\Sentinel-Forge\Sentinel-Forge.exe"
}
finally {
    # Always put tts/ back
    if ($ttsBackup -and (Test-Path $ttsBackup)) {
        Move-Item $ttsBackup "tts" -Force
        Write-Host "tts/ restored." -ForegroundColor Yellow
    }
}
