# PyInstaller spec for Sentinel Forge.
#
# Build with:
#   pyinstaller Sentinel-Forge.spec --clean --noconfirm
#
# Output: book-reader/dist/Sentinel-Forge/Sentinel-Forge.exe
#
# We use a one-folder (not one-file) build so cold-start is fast and
# the large Piper voice + .onnx aren't extracted to a temp dir on every
# launch. The folder ships with the .exe — distribute the whole folder.

import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None
HERE = os.path.dirname(os.path.abspath(SPEC))

# Bundle the sentinel icon + the entire tts/ directory (piper.exe,
# espeak data, voice model). At runtime the app finds them via
# os.path.dirname(__file__) which PyInstaller redirects to _MEIPASS.
datas = [
    (os.path.join(HERE, "sentinel.ico"), "."),
]
if os.path.isdir(os.path.join(HERE, "tts")):
    for root, _dirs, files in os.walk(os.path.join(HERE, "tts")):
        rel_root = os.path.relpath(root, HERE)
        for f in files:
            datas.append((os.path.join(root, f), rel_root))

# tkinterdnd2 ships native Tcl/Tk extensions that need explicit bundling.
try:
    datas += collect_data_files("tkinterdnd2")
except Exception:
    pass

a = Analysis(
    ["book_reader.py"],
    pathex=[HERE],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "send2trash",
        "tkinterdnd2",
        "pyttsx3.drivers",
        "pyttsx3.drivers.sapi5",
        "winsound",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        "matplotlib",
        "numpy",
        "scipy",
        "pandas",
        "PIL.ImageQt",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Sentinel-Forge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,            # UPX often trips Defender; not worth it
    console=False,         # GUI app — no console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(HERE, "sentinel.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Sentinel-Forge",
)
