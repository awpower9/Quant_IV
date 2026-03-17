#!/bin/bash
# ── Quantiv Build Script (Linux/macOS) ───────────────────────────────────────
# Usage: scripts/build.sh [--test] [--no-bindings]

set -e

echo "========================================"
echo "  Quantiv Build Script"
echo "========================================"

# Create build directory
mkdir -p build
cd build

# Configure
cmake .. -DCMAKE_BUILD_TYPE=Release "$@"

# Build
cmake --build . --config Release -j$(nproc 2>/dev/null || sysctl -n hw.ncpu)

# Run tests if requested
if [[ "$1" == "--test" ]]; then
    echo ""
    echo "Running C++ tests..."
    ctest --output-on-failure
fi

cd ..
echo ""
echo "Build complete!"
