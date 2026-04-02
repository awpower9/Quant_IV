# ── pybind11 Bindings ─────────────────────────────────────────────────────────

# 1. Skip searching if pybind11_DIR was already passed externally by pip/setuptools
if(NOT pybind11_DIR)
    execute_process(
        # 2. Add quotes around the executable to safely handle spaces
        COMMAND "${PYTHON_EXECUTABLE}" -m pybind11 --cmakedir
        OUTPUT_VARIABLE pybind11_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
    )
endif()

# Also try the venv python3 if PYTHON_EXECUTABLE is not set
if(NOT pybind11_DIR)
    execute_process(
        COMMAND python3 -m pybind11 --cmakedir # <-- Changed to python3 for macOS
        OUTPUT_VARIABLE pybind11_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
    )
endif()

if(pybind11_DIR)
    file(TO_CMAKE_PATH "${pybind11_DIR}" pybind11_DIR)
    message(STATUS "Found pybind11 cmake dir: ${pybind11_DIR}")
    # 3. Save it properly into CMake's cache so find_package handles spaces accurately
    set(pybind11_DIR "${pybind11_DIR}" CACHE PATH "Pybind11 Config Dir" FORCE)
endif()

# 4. Use standard find_package (it will automatically and safely consume pybind11_DIR)
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(_quantiv_engine
    module.cpp
    bind_option.cpp
    bind_black_scholes.cpp
    bind_binomial.cpp
    bind_trinomial.cpp
    bind_monte_carlo.cpp
    bind_greeks.cpp
    bind_solvers.cpp
    bind_portfolio.cpp  # <-- ADDED THIS!
)

target_link_libraries(_quantiv_engine PRIVATE quantiv_engine)