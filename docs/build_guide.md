# Build Guide

## Prerequisites

- **C++ compiler**: MSVC 2019+, GCC 9+, or Clang 10+ (C++17 required)
- **CMake**: ≥ 3.18
- **Python**: ≥ 3.10
- **Git**: For fetching pybind11 and Google Test

## Full Build (Recommended)

```bash
# 1. Clone and enter the project
cd QUANTIV_FINAL

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

# 3. Install everything (builds C++ extension + installs Python deps)
pip install -e ".[dev]"

# 4. Run tests
pytest tests/python/ -v

# 5. Launch dashboard
python scripts/run_dashboard.py
```

## C++ Only Build

```bash
mkdir build && cd build
cmake .. -DBUILD_BINDINGS=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
ctest --output-on-failure
```

## Troubleshooting

- **pybind11 not found**: Install via `pip install pybind11` or let CMake fetch it.
- **CMake not found**: Install from https://cmake.org/download/
- **MSVC errors**: Ensure you run from a "Developer Command Prompt".
