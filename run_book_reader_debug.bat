@echo off
REM Debug launcher — uses `py` so the console stays open and shows any errors.
REM If the regular shortcut shows "speech unavailable", run this one to see why.
pushd "%~dp0"
py book_reader.py
echo.
echo --- Book Reader exited. Press any key to close this window. ---
pause >nul
popd
