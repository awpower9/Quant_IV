cmake_minimum_required(VERSION 3.18)
project(quantiv VERSION 1.0.0 LANGUAGES CXX)

# ── C++ Standard ─────────────────────────────────────────────────────────────
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# ── Output Directories ───────────────────────────────────────────────────────
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# ── Options ──────────────────────────────────────────────────────────────────
option(BUILD_TESTS    "Build C++ unit tests"           ON)

find_package(gRPC CONFIG REQUIRED)
find_package(Protobuf CONFIG REQUIRED)

# ── Subdirectories ───────────────────────────────────────────────────────────
add_subdirectory(engine)


if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests/cpp)
endif()
