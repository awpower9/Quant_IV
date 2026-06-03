#include "quantiv/models/pro_engine.hpp"
#include <cmath>
#include <algorithm>
#include <complex>
#include <functional>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace quantiv::models {

// ── Internal Math Helpers ──────────────────────────────────────────────────

double ProEngine::normal_cdf(double x) const {
    return 0.5 * std::erfc(-x * std::sqrt(0.5));
}

std::complex<double> ProEngine::heston_char_func(double u, double S, double T, double r, 
                                                 double v0, double kappa, double theta, 
                                                 double sigma, double rho, int j) const {
    std::complex<double> i(0.0, 1.0);
    double u_j = (j == 1) ? 0.5 : -0.5;
    double b_j = (j == 1) ? (kappa - rho * sigma) : kappa;
    double a = kappa * theta;
    
    std::complex<double> d = std::sqrt(std::pow(rho * sigma * u * i - b_j, 2) - 
                                      std::pow(sigma, 2) * (2.0 * u_j * u * i - std::pow(u, 2)));
    
    std::complex<double> g = (b_j - rho * sigma * u * i + d) / (b_j - rho * sigma * u * i - d);
    
    // Use log implementation that avoids discontinuities (standard Heston implementation)
    std::complex<double> exp_dT = std::exp(d * T);
    std::complex<double> C = r * u * i * T + (a / std::pow(sigma, 2)) * 
                             ((b_j - rho * sigma * u * i + d) * T - 2.0 * std::log((1.0 - g * exp_dT) / (1.0 - g)));
    std::complex<double> D = ((b_j - rho * sigma * u * i + d) / std::pow(sigma, 2)) * 
                             ((1.0 - exp_dT) / (1.0 - g * exp_dT));
    
    return std::exp(C + D * v0 + i * u * std::log(S));
}

double ProEngine::numerical_integral(std::function<double(double)> f, double a, double b, int n) const {
    double h = (b - a) / n;
    double sum = f(a) + f(b);
    for (int i = 1; i < n; i++) {
        double x = a + i * h;
        sum += (i % 2 == 0) ? 2 * f(x) : 4 * f(x);
    }
    return (h / 3.0) * sum;
}

// ── Pricing Engines ────────────────────────────────────────────────────────

core::PricingResult ProEngine::price_merton(const core::Option& option, 
                                           const core::MarketData& market,
                                           double lamb, double mu_j, double sigma_j) const {
    auto price_lambda = [&](double S_shocked) {
        double K = option.strike;
        double T = option.expiry;
        double r = market.rate;
        double sigma = market.vol;
        double k_j = std::exp(mu_j + 0.5 * std::pow(sigma_j, 2)) - 1.0;
        double total_price = 0.0;
        double factorial = 1.0;
        for (int n = 0; n < 20; ++n) {
            if (n > 0) factorial *= (n == 0 ? 1 : n);
            double sigma_n = std::sqrt(std::pow(sigma, 2) + (n * std::pow(sigma_j, 2)) / T);
            double r_n = r - lamb * k_j + (n * (mu_j + 0.5 * std::pow(sigma_j, 2))) / T;
            double d1 = (std::log(S_shocked / K) + (r_n + 0.5 * std::pow(sigma_n, 2)) * T) / (sigma_n * std::sqrt(T));
            double d2 = d1 - sigma_n * std::sqrt(T);
            double bs_price = S_shocked * normal_cdf(d1) - K * std::exp(-r_n * T) * normal_cdf(d2);
            double weight = std::exp(-lamb * T) * std::pow(lamb * T, n) / factorial;
            total_price += weight * bs_price;
        }
        if (option.option_type == core::OptionType::Call) return std::max(0.0, total_price);
        else return std::max(0.0, total_price - S_shocked + K * std::exp(-r * T));
    };

    double S = market.spot;
    double dS = std::max(S * 0.001, 1e-4);
    double P = price_lambda(S);
    double P_up = price_lambda(S + dS);
    double P_dn = price_lambda(S - dS);

    core::PricingResult result;
    result.price = P;
    result.greeks["delta"] = (P_up - P_dn) / (2.0 * dS);
    result.greeks["gamma"] = (P_up - 2.0 * P + P_dn) / std::pow(dS, 2);
    return result;
}

core::PricingResult ProEngine::price_heston(const core::Option& option, 
                                           const core::MarketData& market,
                                           double kappa, double theta, double vol_of_vol, double rho) const {
    auto price_lambda = [&](double S_shocked) {
        double K = option.strike;
        double T = option.expiry;
        double r = market.rate;
        double v0 = std::pow(market.vol, 2);
        auto heston_prob = [&](double u, int j) {
            std::complex<double> i(0.0, 1.0);
            std::complex<double> char_func = heston_char_func(u, S_shocked, T, r, v0, kappa, theta, vol_of_vol, rho, j);
            std::complex<double> Integrand = (std::exp(-i * u * std::log(K)) * char_func / (i * u));
            return std::real(Integrand);
        };
        double P1 = 0.5 + (1.0 / M_PI) * numerical_integral([&](double u){ return heston_prob(u, 1); }, 1e-5, 100.0, 500);
        double P2 = 0.5 + (1.0 / M_PI) * numerical_integral([&](double u){ return heston_prob(u, 2); }, 1e-5, 100.0, 500);
        double call_price = S_shocked * P1 - K * std::exp(-r * T) * P2;
        if (option.option_type == core::OptionType::Call) return std::max(0.0, call_price);
        else return std::max(0.0, call_price - S_shocked + K * std::exp(-r * T));
    };

    double S = market.spot;
    double dS = std::max(S * 0.001, 1e-4);
    double P = price_lambda(S);
    double P_up = price_lambda(S + dS);
    double P_dn = price_lambda(S - dS);

    core::PricingResult result;
    result.price = P;
    result.greeks["delta"] = (P_up - P_dn) / (2.0 * dS);
    result.greeks["gamma"] = (P_up - 2.0 * P + P_dn) / std::pow(dS, 2);
    return result;
}

} // namespace quantiv::models