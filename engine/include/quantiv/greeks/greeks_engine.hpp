#pragma once

/**
 * @file greeks_engine.hpp
 * @brief Greeks calculation engine using analytical and finite-difference methods.
 */

#include "quantiv/core/option.hpp"
#include "quantiv/core/market_data.hpp"

#include <map>
#include <string>

namespace quantiv::greeks {

/**
 * @brief Computes option Greeks.
 *
 * For BSM: uses analytical formulas.
 * For tree/MC models: uses finite-difference bumping.
 */
class GreeksEngine {
public:
    /// Compute all Greeks for a BSM-priced option (analytical).
    std::map<std::string, double> compute_bsm_greeks(
        const core::Option& option,
        const core::MarketData& market) const;

    /// Compute delta via finite-difference bump of spot.
    double compute_delta_fd(const core::Option& option,
                            const core::MarketData& market,
                            double bump = 0.01) const;

    /// Compute gamma via finite-difference second derivative.
    double compute_gamma_fd(const core::Option& option,
                            const core::MarketData& market,
                            double bump = 0.01) const;

    /// Compute vega via finite-difference bump of vol.
    double compute_vega_fd(const core::Option& option,
                           const core::MarketData& market,
                           double bump = 0.01) const;

    /// Compute theta via finite-difference bump of time.
    double compute_theta_fd(const core::Option& option,
                            const core::MarketData& market,
                            double bump = 1.0 / 365.0) const;

    /// Compute rho via finite-difference bump of rate.
    double compute_rho_fd(const core::Option& option,
                          const core::MarketData& market,
                          double bump = 0.01) const;
};

}  // namespace quantiv::greeks
