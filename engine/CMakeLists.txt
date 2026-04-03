# --- 1. Define Search Logic for PostgreSQL ---

if(WIN32)
    # Windows: Look in common PostgreSQL and vcpkg install locations
    find_path(PQ_INCLUDE_DIR libpq-fe.h 
        PATHS "C:/Program Files/PostgreSQL/16/include" "C:/vcpkg/installed/x64-windows/include")
    find_library(PQ_LIBRARY libpq 
        PATHS "C:/Program Files/PostgreSQL/16/lib" "C:/vcpkg/installed/x64-windows/lib")
    
    find_path(PQXX_INCLUDE_DIR pqxx/pqxx 
        PATHS "C:/vcpkg/installed/x64-windows/include")
    find_library(PQXX_LIBRARY pqxx 
        PATHS "C:/vcpkg/installed/x64-windows/lib")
else()
    # macOS/Linux: Use Homebrew or System paths
    find_path(PQ_INCLUDE_DIR libpq-fe.h 
        PATHS /opt/homebrew/opt/libpq/include /usr/local/opt/libpq/include /usr/include/postgresql)
    find_library(PQ_LIBRARY pq 
        PATHS /opt/homebrew/opt/libpq/lib /usr/local/opt/libpq/lib /usr/lib)

    find_path(PQXX_INCLUDE_DIR pqxx/pqxx 
        PATHS /opt/homebrew/opt/libpqxx/include /usr/local/opt/libpqxx/include /usr/include)
    find_library(PQXX_LIBRARY pqxx 
        PATHS /opt/homebrew/opt/libpqxx/lib /usr/local/opt/libpqxx/lib /usr/lib)
endif()

# --- 2. Validation Check ---
if(NOT PQ_LIBRARY OR NOT PQXX_LIBRARY)
    message(FATAL_ERROR "PostgreSQL or libpqxx missing! 
    On Mac: brew install libpq libpqxx
    On Linux: sudo apt install libpq-dev libpqxx-dev
    On Windows: Install PostgreSQL and use vcpkg for libpqxx")
endif()

# --- 3. Build the Engine ---
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

# --- 4. Linkage ---
target_include_directories(quantiv_engine PUBLIC 
    include 
    ${PQ_INCLUDE_DIR} 
    ${PQXX_INCLUDE_DIR}
)

target_link_libraries(quantiv_engine PUBLIC ${PQ_LIBRARY} ${PQXX_LIBRARY})