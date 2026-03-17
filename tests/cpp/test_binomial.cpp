/**
 * @file test_binomial.cpp
 * @brief Unit tests for the binomial tree pricing model.
 */

#include <gtest/gtest.h>
#include <cmath>
#include "quantiv/models/binomial.hpp"
#include "quantiv/models/black_scholes.hpp"

using namespace quantiv::core;
using namespace quantiv::models;

class BinomialTest : public ::testing::Test {
protected:
    Option call{100.0, 1.0, OptionType::Call, ExerciseStyle::European};
    MarketData market{100.0, 0.2, 0.05, 0.0};
};

TEST_F(BinomialTest, ConvergesToBSM) {
    BlackScholes bsm;
    double bsm_price = bsm.price(call, market).price;

    Binomial bin(500);  // 500 steps → high accuracy
    double bin_price = bin.price(call, market).price;

    EXPECT_NEAR(bin_price, bsm_price, 0.05);
}

TEST_F(BinomialTest, EuropeanPutConverges) {
    Option put{100.0, 1.0, OptionType::Put, ExerciseStyle::European};

    BlackScholes bsm;
    double bsm_price = bsm.price(put, market).price;

    Binomial bin(500);
    double bin_price = bin.price(put, market).price;

    EXPECT_NEAR(bin_price, bsm_price, 0.05);
}

TEST_F(BinomialTest, AmericanPutGEEuropeanPut) {
    Option euro_put{100.0, 1.0, OptionType::Put, ExerciseStyle::European};
    Option amer_put{100.0, 1.0, OptionType::Put, ExerciseStyle::American};

    Binomial bin(200);
    double euro_price = bin.price(euro_put, market).price;
    double amer_price = bin.price(amer_put, market).price;

    EXPECT_GE(amer_price, euro_price);
}

TEST_F(BinomialTest, TreeHasCorrectSize) {
    Binomial bin(10);
    auto result = bin.price(call, market);

    EXPECT_EQ(result.tree.size(), 11u);  // 0 to 10 inclusive
    EXPECT_EQ(result.tree[10].size(), 11u);  // terminal has N+1 nodes
}

TEST_F(BinomialTest, PricePositive) {
    Binomial bin(100);
    auto result = bin.price(call, market);
    EXPECT_GT(result.price, 0.0);
}
