# QuantIV — Quantitative Options Pricing Platform

A high-performance options pricing platform with a **C++ Engine**, **gRPC Bridge**, **Python Analytics Layer**, and **Plotly Dash UI**.

## Architecture

```
Dash UI  →  Python Analytics  →  gRPC Client/Server  →  C++ Engine
(Layer 4)      (Layer 3)            (Layer 2)           (Layer 1)
```

The system is decoupled using gRPC and Protocol Buffers (`quantiv.proto`). The C++ engine runs as a standalone, high-performance server, while the Python layer acts as a client querying the server for mathematical computations and pricing models.

## Models

| Model | Description |
|---|---|
| Black-Scholes | Analytical closed-form solution |
| Binomial (CRR) | Cox-Ross-Rubinstein binomial tree |
| Trinomial | Three-branch lattice model |
| Monte Carlo | Stochastic simulation with GBM paths |

---

## 🚀 Quick Start Guide

### 1. Prerequisites (C++, Database, & gRPC)

You must install a C++ compiler, CMake, PostgreSQL development libraries, and gRPC dependencies depending on your OS.

**🪟 Windows**
```cmd
# Install Visual Studio Build Tools (C++)
# Install vcpkg for dependencies:
git clone https://github.com/Microsoft/vcpkg.git C:/vcpkg
cd C:/vcpkg
bootstrap-vcpkg.bat
vcpkg integrate install

# Install PostgreSQL connector, gRPC, and Protobuf
vcpkg install libpqxx:x64-windows grpc:x64-windows protobuf:x64-windows
```

**🐧 Linux (Ubuntu/Debian)**
```bash
sudo apt update
sudo apt install build-essential cmake
sudo apt install postgresql libpq-dev libpqxx-dev protobuf-compiler-grpc libgrpc++-dev
```

**🍏 macOS**
```bash
brew install cmake
brew install postgresql libpq libpqxx grpc protobuf
```

### 2. Database Configuration

The C++ engine reads your database connection details from a `.env` file instead of hardcoded strings.

1. **Copy the example configuration:**
   ```bash
   cp .env.example .env     # Linux/macOS
   copy .env.example .env   # Windows
   ```
2. **Start your PostgreSQL Server.**
   If you just installed it, make sure the service is running.
3. **Create the database:**
   ```bash
   createdb -U postgres quantivdb
   ```
4. **Edit `.env`:** Open your new `.env` file and configure your PostgreSQL password, username, and port (usually `5432`).

### 3. Build & Run the C++ gRPC Server

The core pricing engine runs as a separate gRPC server.

```bash
mkdir build
cd build

# On Windows (with vcpkg):
cmake .. -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake
cmake --build . --config Release
# Run the server:
Release\quantiv_server.exe

# On Linux / macOS:
cmake ..
make
# Run the server:
./quantiv_server
```

### 4. Build & Install the Python Client & Dashboard

Open a **new terminal window** to install the Python analytics layer and launch the UI. During installation, `setup.py` automatically generates the Python gRPC stubs from `quantiv.proto`.

```bash
# Create virtual environment
python -m venv .venv
# Activate it
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

# Install dependencies and build gRPC Python stubs
pip install -e ".[dev]"

# Run the Dash UI
python scripts/run_dashboard.py
```
View the interactive dashboard at `http://127.0.0.1:8050`!

---

## Troubleshooting

- **`ModuleNotFoundError: No module named 'quantiv_pb2'`:** The Python gRPC stubs weren't built. Ensure you run `pip install -e .` from the root directory so `setup.py` can generate them.
- **gRPC Server Connection Failed:** Check that your C++ server is running and listening on the expected port defined in `quantiv.proto` or your config.
- **`[DB Warning] Failed to connect:`** Your `quantivdb` database hasn't been created, your PostgreSQL server isn't running, or your `.env` password/port is incorrect. The engine will gracefully fall back to dry-run mode.

## License
MIT
