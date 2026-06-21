@echo off
REM Debug launcher — uses `py` so the console stays open and shows any errors.
REM If the regular shortcut shows "speech unavailable", run this one to see why.
pushd "%~dp0"
py sentinel_personal_development.py
echo.
echo --- Sentinel Forge exited. Press any key to close this window. ---
pause >nul
popd
