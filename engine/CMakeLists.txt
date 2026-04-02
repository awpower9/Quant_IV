# ── Cross-Platform Database Search ──────────────────────────────────────────

if(APPLE)
    # macOS Paths (Homebrew)
    find_path(PQXX_INCLUDE_DIR pqxx/pqxx PATHS /opt/homebrew/opt/libpqxx/include /usr/local/opt/libpqxx/include)
    find_library(PQXX_LIBRARY pqxx PATHS /opt/homebrew/opt/libpqxx/lib /usr/local/opt/libpqxx/lib)

    find_path(PQ_INCLUDE_DIR libpq-fe.h PATHS /opt/homebrew/opt/libpq/include /usr/local/opt/libpq/include)
    find_library(PQ_LIBRARY pq PATHS /opt/homebrew/opt/libpq/lib /usr/local/opt/libpq/lib)
elseif(WIN32)
    # Windows Paths (Standard PostgreSQL Install)
    # Note: Update '16' to your actual Postgres version if different
    find_path(PQXX_INCLUDE_DIR pqxx/pqxx PATHS "C:/Program Files/pqxx/include")
    find_library(PQXX_LIBRARY pqxx PATHS "C:/Program Files/pqxx/lib")

    find_path(PQ_INCLUDE_DIR libpq-fe.h PATHS "C:/Program Files/PostgreSQL/16/include")
    find_library(PQ_LIBRARY libpq PATHS "C:/Program Files/PostgreSQL/16/lib")
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