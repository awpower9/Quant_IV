#pragma once

#include "quantiv/core/option.hpp"
#include "quantiv/core/market_data.hpp"
#include "quantiv/core/pricing_result.hpp"
#include <complex>
#include <functional>

namespace quantiv::models {

/**
 * @brief Advanced Pricing Engine for Jump-Diffusion and Stochastic Volatility.
 */
class ProEngine {
public:
    /// Merton Jump-Diffusion pricing
    core::PricingResult price_merton(const core::Option& option, 
                                    const core::MarketData& market,
                                    double lamb, double mu_j, double sigma_j) const;

    /// Heston Stochastic Volatility pricing
    core::PricingResult price_heston(const core::Option& option, 
                                    const core::MarketData& market,
                                    double kappa, double theta, double vol_of_vol, double rho) const;

private:
    // Internal math helpers
    double normal_cdf(double x) const;
    
    /// Heston Characteristic function
    std::complex<double> heston_char_func(double u, double S, double T, double r, 
                                          double v0, double kappa, double theta, 
                                          double sigma, double rho, int j) const;

    /// Numerical integrator for characteristic functions
    double numerical_integral(std::function<double(double)> f, double a, double b, int n) const;
};

} // namespace quantiv::models