/**
 * @file test_black_scholes.cpp
 * @brief Unit tests for the Black-Scholes pricing model.
 */

#include <gtest/gtest.h>
#include <cmath>
#include "quantiv/models/black_scholes.hpp"

using namespace quantiv::core;
using namespace quantiv::models;

class BlackScholesTest : public ::testing::Test {
protected:
    BlackScholes bsm;

    // Standard test case: ATM European call
    Option call{100.0, 1.0, OptionType::Call, ExerciseStyle::European};
    MarketData market{100.0, 0.2, 0.05, 0.0};
};

TEST_F(BlackScholesTest, ATMCallPrice) {
    auto result = bsm.price(call, market);
    // Expected BSM price ≈ 10.4506
    EXPECT_NEAR(result.price, 10.4506, 0.01);
}

TEST_F(BlackScholesTest, ATMPutPrice) {
    Option put{100.0, 1.0, OptionType::Put, ExerciseStyle::European};
    auto result = bsm.price(put, market);
    // Put-call parity: P = C - S + K*exp(-rT) ≈ 10.4506 - 100 + 95.1229 ≈ 5.5735
    EXPECT_NEAR(result.price, 5.5735, 0.01);
}

TEST_F(BlackScholesTest, PutCallParity) {
    auto call_result = bsm.price(call, market);
    Option put{100.0, 1.0, OptionType::Put};
    auto put_result = bsm.price(put, market);

    double parity_lhs = call_result.price - put_result.price;
    double parity_rhs = market.spot - call.strike * std::exp(-market.rate * call.expiry);
    EXPECT_NEAR(parity_lhs, parity_rhs, 1e-6);
}

TEST_F(BlackScholesTest, DeltaCallPositive) {
    auto result = bsm.price(call, market);
    EXPECT_GT(result.greeks.at("delta"), 0.0);
    EXPECT_LT(result.greeks.at("delta"), 1.0);
}

TEST_F(BlackScholesTest, GammaPositive) {
    auto result = bsm.price(call, market);
    EXPECT_GT(result.greeks.at("gamma"), 0.0);
}

TEST_F(BlackScholesTest, DeepITMCallApproachesIntrinsic) {
    MarketData itm_market{200.0, 0.2, 0.05, 0.0};  // S=200, K=100
    auto result = bsm.price(call, itm_market);
    double intrinsic = 200.0 - 100.0 * std::exp(-0.05 * 1.0);
    EXPECT_NEAR(result.price, intrinsic, 1.0);
}
