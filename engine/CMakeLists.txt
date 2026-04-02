# ── Cross-Platform Database Search ──────────────────────────────────────────

if(WIN32)
    # Find libpq and libpqxx using standard CMake find_package for Windows (via vcpkg)
    find_package(PostgreSQL REQUIRED)
    find_package(libpqxx CONFIG REQUIRED)
    set(PQXX_INCLUDE_DIR)
    set(PQXX_LIBRARY libpqxx::pqxx)
    set(PQ_INCLUDE_DIR ${PostgreSQL_INCLUDE_DIRS})
    set(PQ_LIBRARY ${PostgreSQL_LIBRARIES})
else()
    # 1. Manually find libpqxx and libpq (Supports both Apple Silicon & Intel Macs)
    find_path(PQXX_INCLUDE_DIR pqxx/pqxx PATHS /opt/homebrew/opt/libpqxx/include /usr/local/opt/libpqxx/include)
    find_library(PQXX_LIBRARY pqxx PATHS /opt/homebrew/opt/libpqxx/lib /usr/local/opt/libpqxx/lib)

    find_path(PQ_INCLUDE_DIR libpq-fe.h PATHS /opt/homebrew/opt/libpq/include /usr/local/opt/libpq/include)
    find_library(PQ_LIBRARY pq PATHS /opt/homebrew/opt/libpq/lib /usr/local/opt/libpq/lib)

    # Safety check to ensure Homebrew actually installed them
    if(NOT PQXX_LIBRARY OR NOT PQ_LIBRARY)
        message(FATAL_ERROR "Could not find PostgreSQL or libpqxx. Make sure 'brew install libpq libpqxx' was run.")
    endif()
endif()

if(NOT PQXX_LIBRARY OR NOT PQ_LIBRARY)
    message(FATAL_ERROR "Could not find PostgreSQL or libpqxx. Please ensure they are installed.")
endif()

# ── Create the Engine ───────────────────────────────────────────────────────

add_library(quantiv_engine
    src/core/option.cpp
    src/core/portfolio_engine.cpp
    src/solvers/implied_vol.cpp
    src/utils/math_utils.cpp
    src/models/black_scholes.cpp
    src/models/binomial.cpp
    src/models/trinomial.cpp
    src/models/monte_carlo.cpp
    src/greeks/greeks_engine.cpp
)

target_include_directories(quantiv_engine PUBLIC 
    include
    ${PQXX_INCLUDE_DIR} 
    ${PQ_INCLUDE_DIR}
)

target_link_libraries(quantiv_engine PUBLIC ${PQXX_LIBRARY} ${PQ_LIBRARY})