#pragma once

/**
 * @file implied_vol.hpp
 * @brief Implied volatility solver using Newton-Raphson with Brent fallback.
 */

#include "quantiv/core/option.hpp"
#include "quantiv/core/market_data.hpp"

namespace quantiv::solvers {

/**
 * @brief Solves for the implied volatility given a market price.
 */
class ImpliedVolSolver {
public:
    /// Construct with convergence parameters.
    explicit ImpliedVolSolver(double tol = 1e-8, int max_iter = 100);

    /**
     * @brief Solve for implied volatility.
     * @param option   The option contract.
     * @param market   Market data (vol field is ignored / used as initial guess).
     * @param target_price  The observed market price to match.
     * @return Implied volatility σ, or -1.0 if convergence fails.
     */
    double solve(const core::Option& option,
                 const core::MarketData& market,
                 double target_price) const;

private:
    double tol_;
    int max_iter_;
};

}  // namespace quantiv::solvers
