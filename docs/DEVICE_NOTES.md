# Device Notes – Snapdragon X Windows Laptop

The computer uses a Qualcomm Snapdragon X (Oryon) CPU and Windows 11 on ARM64. The ML workload (CSV preprocessing and three scikit-learn classifiers) is intentionally lightweight and runs on CPU.

## Python environment compatibility

This Streamlit build uses PyArrow for dataframe serialization. The PyPI PyArrow 26.0.1 release provides a CPython 3.13 Windows x64 wheel but does not list a Windows ARM64 wheel. A native ARM64 `pip install` can therefore fall back to building PyArrow from source and require Microsoft C++ Build Tools.

For this project, use Python 3.13 x64 under Windows 11's x64 emulation. The existing native ARM64 Python may remain installed; the project's setup script explicitly selects the generic `py -V:3.13` x64 runtime and verifies `win-amd64`. This is a compatibility compromise, not a claim that x64 emulation is faster than native ARM64.

Windows 11 on Arm supports x64 application emulation through Prism. For this small academic dataset and CPU-based models, this is a reasonable way to retain Streamlit without building PyArrow locally. Native ARM64 execution can be reconsidered when compatible PyArrow wheels are available.

- No TensorFlow, PyTorch, CUDA, GPU or database server is required.
- Random Forest parallel workers are capped at four.
- The raw CGWB CSV remains local and is excluded from Git.
- Setup fails early if the selected Python environment is not x64 or if PyArrow has no binary wheel.
