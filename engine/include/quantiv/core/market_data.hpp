#pragma once

/**
 * @file market_data.hpp
 * @brief Market data container for pricing inputs.
 */

namespace quantiv::core {

/**
 * @brief Holds all market-observable inputs needed for pricing.
 */
struct MarketData {
    double spot;       ///< Current underlying price (S)
    double vol;        ///< Annualized volatility (σ)
    double rate;       ///< Risk-free interest rate (r)
    double dividend;   ///< Continuous dividend yield (q)

    MarketData() = default;

    MarketData(double spot, double vol, double rate, double dividend = 0.0)
        : spot(spot)
        , vol(vol)
        , rate(rate)
        , dividend(dividend) {}
};

}  // namespace quantiv::core
