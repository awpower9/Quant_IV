# QuantIV — Quantitative Options Pricing Platform

A high-performance options pricing platform with a **C++ engine**, **pybind11 bridge**, **Python analytics layer**, and **Plotly Dash UI**.

## Architecture

```
Dash UI  →  Python Analytics  →  pybind11 Bindings  →  C++ Engine
(Layer 4)      (Layer 3)            (Layer 2)           (Layer 1)
```

## Models

| Model | Description |
|---|---|
| Black-Scholes | Analytical closed-form solution |
| Binomial (CRR) | Cox-Ross-Rubinstein binomial tree |
| Trinomial | Three-branch lattice model |
| Monte Carlo | Stochastic simulation with GBM paths |

---

## 🚀 Quick Start Guide

### 1. Prerequisites (C++ & Database)

You must install a C++ compiler, CMake, and the PostgreSQL development libraries depending on your OS:

**🪟 Windows**
```cmd
# Give yourself the Microsoft C++ Build Tools (Install via Visual Studio Installer)
# Then install vcpkg for dependencies (you MUST use vcpkg on Windows!):
git clone https://github.com/Microsoft/vcpkg.git C:/vcpkg
cd C:/vcpkg
bootstrap-vcpkg.bat
vcpkg integrate install
vcpkg install libpqxx:x64-windows
```

**🐧 Linux (Ubuntu/Debian)**
```bash
sudo apt update
sudo apt install build-essential cmake
sudo apt install postgresql libpq-dev  # Installs both DB server and C++ dev headers
```

**🍏 macOS**
```bash
brew install cmake
brew install postgresql libpq libpqxx
```

### 2. Database Configuration

The C++ engine securely reads your database connection details from a `.env` file instead of hardcoded strings.

1. **Copy the example configuration:**
   ```bash
   cp .env.example .env     # Linux/macOS
   copy .env.example .env   # Windows
   ```
2. **Start your PostgreSQL Server.**
   If you just installed it, make sure the service is running (`sudo service postgresql start` on Linux, or `net start postgresql-x64-16` on Windows).
3. **Create the database:**
   ```bash
   createdb -U postgres quantivdb
   ```
4. **Edit `.env`:** Open your new `.env` file and verify your exact PostgreSQL password, username, and port (usually `5432` or `5433`).

### 3. Build & Install (Python)

Create a virtual environment and let `pip` automatically trigger CMake to compile the C++ bindings!

```bash
# Create virtual environment
python -m venv .venv
# Activate it
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

# Install dependencies AND build the C++ extension automatically
pip install -e ".[dev]"
```

>*Note for Windows Users: During pip install, `setup.py` will automatically look for `vcpkg` at `C:/vcpkg` to link `pqxx.dll`. If you installed vcpkg somewhere else, make sure to set the `CMAKE_TOOLCHAIN_FILE` environment variable first.*

### 4. Run the Dashboard

```bash
python scripts/run_dashboard.py
```
View the interactive dashboard at `http://127.0.0.1:8050`!

---

## Troubleshooting

- **`ImportError: DLL load failed` (Windows):** This is handled automatically by `quantiv/__init__.py` which injects `C:\vcpkg\installed\x64-windows\bin` to Python's DLL trace path. If your vcpkg is elsewhere, edit that path in `__init__.py`.
- **`LNK2005 multiply defined symbols` (MSVC):** This is a famous Visual Studio linking issue with `std::string_view` from `pqxx`. It is automatically bypassed in our `bindings/CMakeLists.txt` via `/FORCE:MULTIPLE`.
- **`[DB Warning] Failed to connect:`** Your `quantivdb` database hasn't been created, your PostgreSQL server isn't running, or your `.env` password/port is incorrect. The engine will gracefully fall back to dry-run mode.

## License
MIT
