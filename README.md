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

## Quick Start

### Prerequisites

- **C++ compiler** with C++17 support (MSVC 2019+, GCC 9+, Clang 10+)
- **CMake** ≥ 3.18
- **Python** ≥ 3.10
- **pybind11** ≥ 2.11

### Build & Install

```bash
# Create virtual environment
python -m venv .venv
source .venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

# Install (builds C++ extension automatically)
pip install -e ".[dev]"

# Run the dashboard
python scripts/run_dashboard.py
```

### C++ Only (no Python)

```bash
mkdir build && cd build
cmake .. -DBUILD_BINDINGS=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
ctest --output-on-failure
```

## Project Structure

See [docs/architecture.md](docs/architecture.md) for the full architecture documentation.

## License

MIT
