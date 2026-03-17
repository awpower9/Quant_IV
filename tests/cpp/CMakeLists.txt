# ── C++ Unit Tests (Google Test) ──────────────────────────────────────────────

include(FetchContent)
FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG        v1.14.0
)
FetchContent_MakeAvailable(googletest)

enable_testing()

function(add_quantiv_test test_name test_source)
    add_executable(${test_name} ${test_source})
    target_link_libraries(${test_name} PRIVATE quantiv_engine GTest::gtest_main)
    add_test(NAME ${test_name} COMMAND ${test_name})
endfunction()

add_quantiv_test(test_black_scholes test_black_scholes.cpp)
add_quantiv_test(test_binomial      test_binomial.cpp)
add_quantiv_test(test_trinomial     test_trinomial.cpp)
add_quantiv_test(test_monte_carlo   test_monte_carlo.cpp)
