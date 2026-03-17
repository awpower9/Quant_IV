#pragma once

/**
 * @file monte_carlo.hpp
 * @brief Monte Carlo simulation pricing model.
 */

#include "quantiv/core/option.hpp"
#include "quantiv/core/market_data.hpp"
#include "quantiv/core/pricing_result.hpp"

namespace quantiv::models {

/**
 * @brief Prices options using Monte Carlo simulation with GBM paths.
 *
 * Uses antithetic variates for variance reduction.
 * Stores simulated terminal prices in PricingResult::path_prices.
 */
class MonteCarlo {
public:
    /// Construct with the number of simulation paths and optional seed.
    explicit MonteCarlo(int num_paths = 100000, unsigned int seed = 42);

    /// Price the option using Monte Carlo simulation.
    core::PricingResult price(const core::Option& option,
                              const core::MarketData& market) const;

    int num_paths() const { return num_paths_; }
    void set_num_paths(int n) { num_paths_ = n; }

    unsigned int seed() const { return seed_; }
    void set_seed(unsigned int s) { seed_ = s; }

private:
    int num_paths_;
    unsigned int seed_;
};

}  // namespace quantiv::models
