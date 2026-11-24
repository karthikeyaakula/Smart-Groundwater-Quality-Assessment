@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo ======================================================
echo  SMART GROUNDWATER QUALITY - WINDOWS SETUP
echo ======================================================
echo.
echo This setup targets CPython 3.13 x64 under Windows 11 on Arm.
echo Streamlit requires PyArrow. PyPI currently publishes a CPython 3.13 Windows x64 wheel,
echo but not a corresponding Windows ARM64 wheel, so an ARM64 pip install tries to build PyArrow.
echo.

where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: The Python launcher 'py' was not found.
  echo Install Python 3.13 Windows installer (64-bit / x64) and enable the Python launcher.
  goto :error
)

echo Checking Python 3.13 x64 runtime...
py -V:3.13 -c "import sys,sysconfig,platform; print('Python:',sys.version); print('Platform:',sysconfig.get_platform()); print('Machine:',platform.machine()); sys.exit(0 if sys.version_info[:2] == (3,13) and sysconfig.get_platform().lower().endswith('amd64') else 1)"
if errorlevel 1 (
  echo.
  echo ERROR: Python 3.13 x64 was not found or did not pass the architecture check.
  echo Your current Python 3.13 ARM64 installation can remain installed.
  echo Install the separate Windows installer (64-bit / x64), NOT the ARM64 installer:
  echo https://www.python.org/downloads/release/python-31317/
  echo Then close and reopen VS Code and run this setup again.
  goto :error
)

if exist ".venv\Scripts\python.exe" (
  echo Checking existing virtual environment...
  .venv\Scripts\python.exe -c "import sysconfig; print('Existing venv platform:',sysconfig.get_platform()); sys.exit(0 if sysconfig.get_platform().lower().endswith('amd64') else 1)"
  if errorlevel 1 (
    echo Existing .venv is ARM64 or incompatible. Recreating it with Python x64...
    rmdir /s /q .venv
    if errorlevel 1 goto :error
  )
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating x64 project virtual environment...
  py -V:3.13 -m venv .venv
  if errorlevel 1 goto :error
)

echo.
echo Verifying the virtual environment architecture...
.venv\Scripts\python.exe -c "import sys,sysconfig; print('Venv Python:',sys.version); print('Venv platform:',sysconfig.get_platform()); sys.exit(0 if sys.version_info[:2] == (3,13) and sysconfig.get_platform().lower().endswith('amd64') else 1)"
if errorlevel 1 goto :error

echo.
echo Upgrading pip...
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto :error

echo.
echo Installing project dependencies (PyArrow must use a prebuilt wheel)...
.venv\Scripts\python.exe -m pip install --only-binary=pyarrow -r requirements.txt
if errorlevel 1 (
  echo.
  echo Dependency installation failed. Check the first pip error above.
  echo The setup intentionally refuses to compile PyArrow from source.
  goto :error
)

echo.
echo Verifying core imports...
.venv\Scripts\python.exe -c "import pandas,numpy,sklearn,matplotlib,joblib,streamlit,pyarrow; print('pandas',pandas.__version__); print('numpy',numpy.__version__); print('scikit-learn',sklearn.__version__); print('streamlit',streamlit.__version__); print('pyarrow',pyarrow.__version__)"
if errorlevel 1 goto :error

echo.
echo ======================================================
echo Setup completed successfully.
echo Next: place the CGWB CSV in data\, then run inspect_data.bat.
echo After checking the nitrate header and unit, run train.bat and run_app.bat.
echo ======================================================
pause
exit /b 0

:error
echo.
echo Setup failed. No model training was started.
pause
exit /b 1
