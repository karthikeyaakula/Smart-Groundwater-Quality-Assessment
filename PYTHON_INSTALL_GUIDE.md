# Python setup for Snapdragon X (Windows 11 ARM64)

## Why the setup uses x64 Python

This project uses Streamlit, which requires PyArrow for dataframe serialization. The PyArrow 26.0.1 PyPI release includes a CPython 3.13 Windows x64 wheel (`win_amd64`) but does not list a Windows ARM64 wheel (`win_arm64`). With native ARM64 Python, pip therefore downloads the source distribution and attempts a local build. That build can fail when Microsoft C++ Build Tools are not installed.

For this Streamlit-based student project, the simplest reliable route is to install **Python 3.13 x64** and run it under Windows 11 on Arm's x64 emulation. Your existing Python 3.13 ARM64 installation can remain installed; both architectures can coexist.

Windows 11 on Arm supports x64 application emulation. This project is small, so the x64 environment is a practical compatibility trade-off. Native ARM64 would be preferable for performance if all required binary wheels, including PyArrow, become available.

## Install the correct Python build

1. Open the official Python 3.13.17 release page: https://www.python.org/downloads/release/python-31317/
2. Download **Windows installer (64-bit)**. Do NOT choose **Windows installer (ARM64)**.
3. Run the installer. Enable the Python Launcher option; adding Python to PATH is also useful.
4. Close and reopen VS Code.
5. In PowerShell, run:

```powershell
py -0p
py -V:3.13 -c "import sys,sysconfig,platform; print(sys.version); print(sysconfig.get_platform()); print(platform.machine())"
```

The second command should report a platform ending in `win-amd64`. If it reports `win-arm64`, the x64 runtime is not yet selected/installed.

## Run project setup

From the project folder:

```powershell
.\setup_windows.bat
```

The setup script explicitly selects `py -V:3.13`, verifies `win-amd64`, recreates an old ARM64 `.venv` if necessary, and installs PyArrow using a binary wheel only. It will stop with a clear message rather than attempt a source build.

After setup succeeds, put the official CGWB CSV in `data/` and run:

```powershell
.\inspect_data.bat
```

Confirm the nitrate header and unit before running `train.bat`.
