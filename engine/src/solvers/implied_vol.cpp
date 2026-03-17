/**
 * @file implied_vol.cpp
 * @brief Implied volatility solver using Newton-Raphson.
 */

#include "quantiv/solvers/implied_vol.hpp"
#include "quantiv/models/black_scholes.hpp"

#include <cmath>
#include <algorithm>

namespace quantiv::solvers {

using namespace quantiv::core;

ImpliedVolSolver::ImpliedVolSolver(double tol, int max_iter)
    : tol_(tol), max_iter_(max_iter) {}

double ImpliedVolSolver::solve(const Option& option,
                               const MarketData& market,
                               double target_price) const {
    models::BlackScholes bsm;

    // Initial guess: Brenner-Subrahmanyam approximation
    double sigma = std::sqrt(2.0 * 3.14159265 / option.expiry)
                 * target_price / market.spot;
    sigma = std::clamp(sigma, 0.01, 5.0);

    MarketData mkt = market;

    for (int i = 0; i < max_iter_; ++i) {
        mkt.vol = sigma;
        auto result = bsm.price(option, mkt);

        double diff = result.price - target_price;
        if (std::abs(diff) < tol_) {
            return sigma;
        }

        // Vega for Newton step (un-normalized, per unit vol)
        double vega = result.greeks.count("vega")
                    ? result.greeks.at("vega") * 100.0  // undo /100 scaling
                    : 1e-10;

        if (std::abs(vega) < 1e-12) {
            // Vega too small — switch to bisection-like step
            sigma += (diff > 0 ? -0.01 : 0.01);
        } else {
            sigma -= diff / vega;
        }

        // Clamp to reasonable range
        sigma = std::clamp(sigma, 1e-6, 10.0);
    }

    return -1.0;  // convergence failure
}

}  // namespace quantiv::solvers
