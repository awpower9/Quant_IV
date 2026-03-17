/**
 * @file test_monte_carlo.cpp
 * @brief Unit tests for the Monte Carlo pricing model.
 */

#include <gtest/gtest.h>
#include <cmath>
#include "quantiv/models/monte_carlo.hpp"
#include "quantiv/models/black_scholes.hpp"

using namespace quantiv::core;
using namespace quantiv::models;

class MonteCarloTest : public ::testing::Test {
protected:
    Option call{100.0, 1.0, OptionType::Call, ExerciseStyle::European};
    MarketData market{100.0, 0.2, 0.05, 0.0};
};

TEST_F(MonteCarloTest, ConvergesToBSM) {
    BlackScholes bsm;
    double bsm_price = bsm.price(call, market).price;

    MonteCarlo mc(500000, 42);
    double mc_price = mc.price(call, market).price;

    // MC should converge within ~0.5% with 500K paths
    EXPECT_NEAR(mc_price, bsm_price, bsm_price * 0.01);
}

TEST_F(MonteCarloTest, DeterministicWithSeed) {
    MonteCarlo mc1(100000, 42);
    MonteCarlo mc2(100000, 42);

    double price1 = mc1.price(call, market).price;
    double price2 = mc2.price(call, market).price;

    EXPECT_DOUBLE_EQ(price1, price2);
}

TEST_F(MonteCarloTest, DifferentSeedsDifferentPrices) {
    MonteCarlo mc1(100000, 42);
    MonteCarlo mc2(100000, 123);

    double price1 = mc1.price(call, market).price;
    double price2 = mc2.price(call, market).price;

    EXPECT_NE(price1, price2);
}

TEST_F(MonteCarloTest, PathPricesStored) {
    MonteCarlo mc(1000, 42);
    auto result = mc.price(call, market);

    EXPECT_EQ(result.path_prices.size(), 1000u);

    for (double p : result.path_prices) {
        EXPECT_GT(p, 0.0);
    }
}

TEST_F(MonteCarloTest, PutPricePositive) {
    Option put{100.0, 1.0, OptionType::Put};
    MonteCarlo mc(100000, 42);
    auto result = mc.price(put, market);
    EXPECT_GT(result.price, 0.0);
}
