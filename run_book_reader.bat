@echo off
REM Launches Sentinel Forge as a real Windows desktop app (no console).
REM Avoids the broken Windows Store pythonw stub at
REM   %LOCALAPPDATA%\Microsoft\WindowsApps\pythonw.exe
REM which is what where pythonw finds first on many setups.
pushd "%~dp0"

REM Preferred: pyw — the Python Launcher's GUI variant. Resolves to
REM the user's installed Python via the standard py launcher.
where pyw >nul 2>nul
if %ERRORLEVEL%==0 (
  start "" pyw "%~dp0book_reader.py"
  goto :done
)

REM Fallback 1: canonical install location for Python 3.13.
if exist "%LOCALAPPDATA%\Programs\Python\Python313\pythonw.exe" (
  start "" "%LOCALAPPDATA%\Programs\Python\Python313\pythonw.exe" "%~dp0book_reader.py"
  goto :done
)

REM Fallback 2: same install for Python 3.12.
if exist "%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe" (
  start "" "%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe" "%~dp0book_reader.py"
  goto :done
)

REM Last resort: the py launcher in console mode so errors are visible.
start "" py "%~dp0book_reader.py"

:done
popd