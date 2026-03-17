/**
 * @file test_trinomial.cpp
 * @brief Unit tests for the trinomial tree pricing model.
 */

#include <gtest/gtest.h>
#include "quantiv/models/trinomial.hpp"
#include "quantiv/models/black_scholes.hpp"

using namespace quantiv::core;
using namespace quantiv::models;

class TrinomialTest : public ::testing::Test {
protected:
    Option call{100.0, 1.0, OptionType::Call, ExerciseStyle::European};
    MarketData market{100.0, 0.2, 0.05, 0.0};
};

TEST_F(TrinomialTest, ConvergesToBSM) {
    BlackScholes bsm;
    double bsm_price = bsm.price(call, market).price;

    Trinomial tri(300);
    double tri_price = tri.price(call, market).price;

    EXPECT_NEAR(tri_price, bsm_price, 0.1);
}

TEST_F(TrinomialTest, PricePositive) {
    Trinomial tri(100);
    auto result = tri.price(call, market);
    EXPECT_GT(result.price, 0.0);
}

TEST_F(TrinomialTest, AmericanPutGEEuropean) {
    Option euro_put{100.0, 1.0, OptionType::Put, ExerciseStyle::European};
    Option amer_put{100.0, 1.0, OptionType::Put, ExerciseStyle::American};

    Trinomial tri(200);
    double euro_price = tri.price(euro_put, market).price;
    double amer_price = tri.price(amer_put, market).price;

    EXPECT_GE(amer_price, euro_price);
}
