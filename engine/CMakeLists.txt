# ── Cross-Platform Database Search ──────────────────────────────────────────

if(WIN32)
    # Find libpq and libpqxx using standard CMake find_package for Windows (via vcpkg)
    find_package(PostgreSQL REQUIRED)
    find_package(libpqxx CONFIG REQUIRED)
    set(PQ_LIBRARY PostgreSQL::PostgreSQL)
    set(PQXX_LIBRARY libpqxx::pqxx)
else()
    # ── Standard Linux/Mac Search ──────────────────────────────────────
    find_package(PostgreSQL REQUIRED)
    
    # Try finding libpqxx via config (modern / Render / New Homebrew)
    find_package(libpqxx CONFIG QUIET)
    
    if(libpqxx_FOUND)
        set(PQXX_LIBRARY libpqxx::pqxx)
    else()
        # Fallback to manual search (Older systems / Custom layouts)
        find_library(PQXX_LIBRARY pqxx PATHS /usr/lib /usr/local/lib /opt/homebrew/lib)
        find_path(PQXX_INCLUDE_DIR pqxx/pqxx PATHS /usr/include /usr/local/include /opt/homebrew/include)
        
        if(NOT PQXX_LIBRARY)
            message(FATAL_ERROR "Could not find libpqxx headers or library. Please install libpqxx-dev.")
        endif()
    endif()
    
    set(PQ_LIBRARY PostgreSQL::PostgreSQL)
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
    src/models/pro_engine.cpp
)

target_include_directories(quantiv_engine PUBLIC 
    include
    ${PQXX_INCLUDE_DIR} 
    ${PQ_INCLUDE_DIR}
)

target_link_libraries(quantiv_engine PUBLIC ${PQXX_LIBRARY} ${PQ_LIBRARY})