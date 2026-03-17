#pragma once

/**
 * @file trinomial.hpp
 * @brief Trinomial tree pricing model.
 */

#include "quantiv/core/option.hpp"
#include "quantiv/core/market_data.hpp"
#include "quantiv/core/pricing_result.hpp"

namespace quantiv::models {

/**
 * @brief Prices options using a trinomial lattice.
 *
 * Three branches (up, middle, down) provide faster convergence
 * than the binomial tree for the same number of steps.
 */
class Trinomial {
public:
    /// Construct with the number of time steps.
    explicit Trinomial(int steps = 100);

    /// Price the option using the trinomial tree.
    core::PricingResult price(const core::Option& option,
                              const core::MarketData& market) const;

    int steps() const { return steps_; }
    void set_steps(int steps) { steps_ = steps; }

private:
    int steps_;
};

}  // namespace quantiv::models
