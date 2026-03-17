#pragma once

/**
 * @file black_scholes.hpp
 * @brief Black-Scholes-Merton analytical pricing model.
 */

#include "quantiv/core/option.hpp"
#include "quantiv/core/market_data.hpp"
#include "quantiv/core/pricing_result.hpp"

namespace quantiv::models {

/**
 * @brief Computes European option prices using the BSM closed-form solution.
 *
 * Supports continuous dividend yield. Computes Greeks analytically.
 */
class BlackScholes {
public:
    /// Price the option and compute analytical Greeks.
    core::PricingResult price(const core::Option& option,
                              const core::MarketData& market) const;

private:
    double compute_d1(double S, double K, double r, double q,
                      double sigma, double T) const;
    double compute_d2(double d1, double sigma, double T) const;
};

}  // namespace quantiv::models
