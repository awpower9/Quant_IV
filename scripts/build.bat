@echo off
REM ── Quantiv Build Script (Windows) ─────────────────────────────────────────
REM Usage: scripts\build.bat [--test] [--no-bindings]

echo ========================================
echo   Quantiv Build Script
echo ========================================

REM Create build directory
if not exist build mkdir build
cd build

REM Configure
cmake .. -DCMAKE_BUILD_TYPE=Release %*

REM Build
cmake --build . --config Release

REM Run tests if requested
if "%1"=="--test" (
    echo.
    echo Running C++ tests...
    ctest --output-on-failure --build-config Release
)

cd ..
echo.
echo Build complete!
