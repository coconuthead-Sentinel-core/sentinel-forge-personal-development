# install_tts.ps1 — download the Piper neural-TTS engine + a default
# voice model, and lay them out under ./tts where book_reader.py expects
# to find piper.exe and the .onnx voice file.
#
# Why this isn't checked into git: the bundle is ~100 MB, dominated by
# the en_US-amy-medium voice model (60 MB). Distributing binaries via
# git is bad practice and makes the repo huge.
#
# Run from the repo root:
#   powershell -ExecutionPolicy Bypass -File scripts\install_tts.ps1

param(
    [string]$Voice = "en_US-amy-medium",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$repoRoot  = Resolve-Path "$PSScriptRoot\.."
$ttsDir    = Join-Path $repoRoot "tts"
$voicesDir = Join-Path $ttsDir "voices"

if ((Test-Path $ttsDir) -and (-not $Force)) {
    Write-Host "tts/ already exists. Use -Force to reinstall." -ForegroundColor Yellow
    exit 0
}

New-Item -ItemType Directory -Path $ttsDir    -Force | Out-Null
New-Item -ItemType Directory -Path $voicesDir -Force | Out-Null

# --- 1. Piper engine binary (Windows x64) ---------------------------
$piperRelease = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"
$piperZip     = Join-Path $env:TEMP "piper_windows_amd64.zip"

Write-Host "Downloading Piper engine..."
Invoke-WebRequest -Uri $piperRelease -OutFile $piperZip -UseBasicParsing

Write-Host "Extracting Piper into $ttsDir ..."
Expand-Archive -Path $piperZip -DestinationPath $ttsDir -Force
# Piper zip extracts to tts/piper/ — flatten it.
$inner = Join-Path $ttsDir "piper"
if (Test-Path $inner) {
    Get-ChildItem $inner -Force | Move-Item -Destination $ttsDir -Force
    Remove-Item $inner -Recurse -Force
}
Remove-Item $piperZip -Force

# --- 2. Default voice model ----------------------------------------
# Piper voices follow the URL pattern below. en_US-amy-medium is a
# good neutral default; users can swap for any other Piper voice.
$voiceBase = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium"
$voiceOnnx = "$voiceBase/en_US-amy-medium.onnx"
$voiceJson = "$voiceBase/en_US-amy-medium.onnx.json"

Write-Host "Downloading voice model: $Voice ..."
Invoke-WebRequest -Uri $voiceOnnx -OutFile (Join-Path $voicesDir "$Voice.onnx")      -UseBasicParsing
Invoke-WebRequest -Uri $voiceJson -OutFile (Join-Path $voicesDir "$Voice.onnx.json") -UseBasicParsing

Write-Host ""
Write-Host "Piper TTS installed under: $ttsDir"
Write-Host "Voice:                    $Voice"
Write-Host "Run 'py -3 book_reader.py' to use it."
