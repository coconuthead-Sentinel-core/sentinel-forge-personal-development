# install_book_reader_shortcut.ps1
# Creates a Desktop shortcut named "Book Reader" that launches the app.

$root        = (Resolve-Path "$PSScriptRoot\..").Path
$desktop     = [Environment]::GetFolderPath("Desktop")
$lnkPath     = Join-Path $desktop "Book Reader.lnk"

$wsh = New-Object -ComObject WScript.Shell
$lnk = $wsh.CreateShortcut($lnkPath)
$lnk.TargetPath       = Join-Path $root "run_book_reader.bat"
$lnk.WorkingDirectory = $root
$lnk.IconLocation     = "shell32.dll,23"    # book-style icon
$lnk.Description      = "Memory Cube Book Reader"
$lnk.Save()

Write-Host "Created Desktop shortcut: $lnkPath"
