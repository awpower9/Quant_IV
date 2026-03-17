# ── pybind11 Bindings ─────────────────────────────────────────────────────────

# Find pybind11 — prefer pip-installed version via pybind11's cmake helper
execute_process(
    COMMAND ${PYTHON_EXECUTABLE} -m pybind11 --cmakedir
    OUTPUT_VARIABLE pybind11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    ERROR_QUIET
)

# Also try the venv python if PYTHON_EXECUTABLE is not set
if(NOT pybind11_DIR)
    execute_process(
        COMMAND python -m pybind11 --cmakedir
        OUTPUT_VARIABLE pybind11_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
    )
endif()

if(pybind11_DIR)
    message(STATUS "Found pybind11 cmake dir: ${pybind11_DIR}")
    find_package(pybind11 CONFIG REQUIRED PATHS ${pybind11_DIR} NO_DEFAULT_PATH)
else()
    find_package(pybind11 CONFIG REQUIRED)
endif()

pybind11_add_module(_quantiv_engine
    module.cpp
    bind_option.cpp
    bind_black_scholes.cpp
    bind_binomial.cpp
    bind_trinomial.cpp
    bind_monte_carlo.cpp
    bind_greeks.cpp
    bind_solvers.cpp
)

target_link_libraries(_quantiv_engine PRIVATE quantiv_engine)
