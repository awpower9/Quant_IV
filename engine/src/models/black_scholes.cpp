/**
 * @file black_scholes.cpp
 * @brief Black-Scholes-Merton analytical pricing implementation.
 */

#include "quantiv/models/black_scholes.hpp"
#include "quantiv/utils/math_utils.hpp"

#include <cmath>

namespace quantiv::models {

using namespace quantiv::core;
using quantiv::utils::norm_cdf;
using quantiv::utils::norm_pdf;

double BlackScholes::compute_d1(double S, double K, double r, double q,
                                double sigma, double T) const {
    return (std::log(S / K) + (r - q + 0.5 * sigma * sigma) * T)
           / (sigma * std::sqrt(T));
}

double BlackScholes::compute_d2(double d1, double sigma, double T) const {
    return d1 - sigma * std::sqrt(T);
}

PricingResult BlackScholes::price(const Option& option,
                                  const MarketData& market) const {
    PricingResult result;

    double S     = market.spot;
    double K     = option.strike;
    double r     = market.rate;
    double q     = market.dividend;
    double sigma = market.vol;
    double T     = option.expiry;

    double d1 = compute_d1(S, K, r, q, sigma, T);
    double d2 = compute_d2(d1, sigma, T);

    double discount   = std::exp(-r * T);
    double div_factor = std::exp(-q * T);

    if (option.option_type == OptionType::Call) {
        result.price = S * div_factor * norm_cdf(d1)
                     - K * discount * norm_cdf(d2);

        // Analytical Greeks
        result.greeks["delta"] = div_factor * norm_cdf(d1);
        result.greeks["gamma"] = div_factor * norm_pdf(d1)
                               / (S * sigma * std::sqrt(T));
        result.greeks["vega"]  = S * div_factor * norm_pdf(d1)
                               * std::sqrt(T) / 100.0;  // per 1% vol
        result.greeks["theta"] = (-(S * div_factor * norm_pdf(d1) * sigma)
                                  / (2.0 * std::sqrt(T))
                                 - r * K * discount * norm_cdf(d2)
                                 + q * S * div_factor * norm_cdf(d1))
                                / 365.0;  // per day
        result.greeks["rho"]   = K * T * discount * norm_cdf(d2) / 100.0;

    } else {  // Put
        result.price = K * discount * norm_cdf(-d2)
                     - S * div_factor * norm_cdf(-d1);

        result.greeks["delta"] = div_factor * (norm_cdf(d1) - 1.0);
        result.greeks["gamma"] = div_factor * norm_pdf(d1)
                               / (S * sigma * std::sqrt(T));
        result.greeks["vega"]  = S * div_factor * norm_pdf(d1)
                               * std::sqrt(T) / 100.0;
        result.greeks["theta"] = (-(S * div_factor * norm_pdf(d1) * sigma)
                                  / (2.0 * std::sqrt(T))
                                 + r * K * discount * norm_cdf(-d2)
                                 - q * S * div_factor * norm_cdf(-d1))
                                / 365.0;
        result.greeks["rho"]   = -K * T * discount * norm_cdf(-d2) / 100.0;
    }

    return result;
}

}  // namespace quantiv::models
