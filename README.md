# QuantIV - Quantitative Options Pricing Platform

QuantIV is a high-performance options pricing and risk analytics platform. Designed for scalability and low latency, it features a strictly decoupled architecture where computationally intensive numerical methods are executed in a C++ backend, while higher-level analytics, data visualization, and user interactions are handled by a Python frontend.

## Architectural Layers

The platform is strictly divided into four distinct computational layers:

### Layer 1: C++ Core Pricing Engine
The foundation of the platform is a standalone, C++20-compliant high-performance engine located in `engine/`. This layer is responsible for all heavy numerical computation and quantitative modeling.
- **Models**: Implements closed-form solutions (Black-Scholes), lattice models (Cox-Ross-Rubinstein Binomial and Trinomial trees), and stochastic simulations (Monte Carlo). Advanced stochastic volatility and jump-diffusion models (Heston, Merton) are also supported via finite difference methods.
- **Risk Metrics (Greeks)**: Computes first and second-order sensitivities (Delta, Gamma, Vega, Theta, Rho) using both analytical derivatives and bump-and-revalue numerical differentiation.
- **Persistence**: Integrates with PostgreSQL via `libpqxx` to securely handle persistent state and historical market configurations, abstracting connection details away from the application code via `.env`.

### Layer 2: gRPC Inter-Process Bridge
To completely isolate the C++ memory space from the Python runtime, the system uses gRPC and Protocol Buffers (`quantiv.proto`). 
- **Protocol**: Defines strict data schemas (`Option`, `MarketData`) and the `QuantivPricer` remote procedure call service. 
- **Server**: The C++ layer runs a highly concurrent gRPC server (`quantiv_server`), listening for remote pricing requests, distributing workloads, and returning structured `PricingResponse` objects containing calculated prices and Greeks.

### Layer 3: Python Analytics Middle-Tier
Located in `quantiv/`, this layer acts as the analytical brain connecting the raw backend to the user interface.
- **Client Integration**: Wraps the auto-generated Python gRPC stubs, handling serialization, error recovery, and connection pooling via `grpc_client.py` and `pricer.py`.
- **Advanced Analytics**: Implements higher-order logic that relies on iterative backend queries, including Implied Volatility surface generation (`iv_surface.py`), aggregate portfolio risk reporting (`risk_reporter.py`), and multi-leg strategy construction (`strategy_builder.py`).

### Layer 4: Plotly Dash User Interface
The user-facing presentation layer located in `dashboard/`.
- **Interactivity**: Built with Plotly Dash to provide real-time updates of option chains, Greek profiles, and volatility surfaces.
- **State Management**: Uses robust Dash callback graphs to manage application state without blocking the async gRPC requests to the backend.

---

## Technical Prerequisites

To compile and run the platform, the following toolchains are strictly required:

- **Compiler**: A modern C++ compiler supporting C++20 (MSVC, GCC, or Clang).
- **Build System**: CMake (version 3.18 or higher).
- **Database**: PostgreSQL server and development headers (`libpq` and `libpqxx`).
- **RPC Framework**: gRPC and Protocol Buffers.
- **Python**: Python 3.10 or higher.

## System Build Guide

### 1. Database Configuration

The C++ engine securely reads your database connection details from a `.env` file.

1. Copy the template configuration file: `cp .env.example .env` (or `copy .env.example .env` on Windows).
2. Start your PostgreSQL daemon.
3. Create the necessary database: `createdb -U postgres quantivdb`
4. Modify the `.env` file to match your active PostgreSQL credentials and port.

### 2. Compiling the C++ Backend Server

The engine must be compiled into a standalone executable server.

**Windows (using vcpkg):**
```cmd
mkdir build
cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake
cmake --build . --config Release
Release\quantiv_server.exe
```

**Linux / macOS:**
```bash
mkdir build
cd build
cmake ..
make
./quantiv_server
```

### 3. Installing the Python Analytics & UI

With the C++ server running in the background, open a new terminal session to build the Python environment. The standard package installation automatically invokes `grpc_tools.protoc` to generate the required Python stubs from the protocol buffer definitions.

```bash
python -m venv .venv

# Windows activation
.venv\Scripts\activate
# Linux/macOS activation
# source .venv/bin/activate

pip install -e ".[dev]"
python scripts/run_dashboard.py
```

Navigate to `http://127.0.0.1:8050` to access the interactive dashboard.

## License
MIT
