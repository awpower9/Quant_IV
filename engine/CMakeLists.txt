# ── Engine Core Library ───────────────────────────────────────────────────

# 1. Manually find libpqxx and libpq (Supports both Apple Silicon & Intel Macs)
find_path(PQXX_INCLUDE_DIR pqxx/pqxx PATHS /opt/homebrew/opt/libpqxx/include /usr/local/opt/libpqxx/include)
find_library(PQXX_LIBRARY pqxx PATHS /opt/homebrew/opt/libpqxx/lib /usr/local/opt/libpqxx/lib)

find_path(PQ_INCLUDE_DIR libpq-fe.h PATHS /opt/homebrew/opt/libpq/include /usr/local/opt/libpq/include)
find_library(PQ_LIBRARY pq PATHS /opt/homebrew/opt/libpq/lib /usr/local/opt/libpq/lib)

# Safety check to ensure Homebrew actually installed them
if(NOT PQXX_LIBRARY OR NOT PQ_LIBRARY)
    message(FATAL_ERROR "Could not find PostgreSQL or libpqxx. Make sure 'brew install libpq libpqxx' was run.")
endif()

# 2. Create the engine library
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

# 3. PUBLICLY Include our own headers AND the Postgres headers!
target_include_directories(quantiv_engine PUBLIC 
    include
    ${PQXX_INCLUDE_DIR} 
    ${PQ_INCLUDE_DIR}
)

# 4. Link the database libraries to our engine
target_link_libraries(quantiv_engine PUBLIC ${PQXX_LIBRARY} ${PQ_LIBRARY})