# ── Engine Library ────────────────────────────────────────────────────────────

set(ENGINE_SOURCES
    src/core/option.cpp
    src/models/black_scholes.cpp
    src/models/binomial.cpp
    src/models/trinomial.cpp
    src/models/monte_carlo.cpp
    src/greeks/greeks_engine.cpp
    src/solvers/implied_vol.cpp
    src/utils/math_utils.cpp
)

add_library(quantiv_engine STATIC ${ENGINE_SOURCES})

target_include_directories(quantiv_engine
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

target_compile_features(quantiv_engine PUBLIC cxx_std_17)

# ── Compiler Warnings ────────────────────────────────────────────────────────
if(MSVC)
    target_compile_options(quantiv_engine PRIVATE /W4)
else()
    target_compile_options(quantiv_engine PRIVATE -Wall -Wextra -Wpedantic)
endif()
