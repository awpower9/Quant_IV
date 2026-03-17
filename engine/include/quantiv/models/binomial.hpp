#pragma once

/**
 * @file binomial.hpp
 * @brief Cox-Ross-Rubinstein (CRR) binomial tree pricing model.
 */

#include "quantiv/core/option.hpp"
#include "quantiv/core/market_data.hpp"
#include "quantiv/core/pricing_result.hpp"

namespace quantiv::models {

/**
 * @brief Prices options using a CRR binomial lattice.
 *
 * Supports European and American exercise. Stores full tree
 * in PricingResult::tree for visualization.
 */
class Binomial {
public:
    /// Construct with the number of time steps.
    explicit Binomial(int steps = 100);

    /// Price the option using the binomial tree.
    core::PricingResult price(const core::Option& option,
                              const core::MarketData& market) const;

    /// Get the number of steps.
    int steps() const { return steps_; }

    /// Set the number of steps.
    void set_steps(int steps) { steps_ = steps; }

private:
    int steps_;
};

}  // namespace quantiv::models
