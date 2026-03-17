/**
 * @file monte_carlo.cpp
 * @brief Monte Carlo simulation pricing implementation.
 */

#include "quantiv/models/monte_carlo.hpp"

#include <cmath>
#include <algorithm>
#include <random>
#include <numeric>

namespace quantiv::models {

using namespace quantiv::core;

MonteCarlo::MonteCarlo(int num_paths, unsigned int seed)
    : num_paths_(num_paths), seed_(seed) {}

PricingResult MonteCarlo::price(const Option& option,
                                const MarketData& market) const {
    PricingResult result;

    double S     = market.spot;
    double K     = option.strike;
    double r     = market.rate;
    double q     = market.dividend;
    double sigma = market.vol;
    double T     = option.expiry;

    std::mt19937 gen(seed_);
    std::normal_distribution<double> dist(0.0, 1.0);

    double drift = (r - q - 0.5 * sigma * sigma) * T;
    double diffusion = sigma * std::sqrt(T);
    double discount = std::exp(-r * T);

    result.path_prices.reserve(num_paths_);
    double sum_payoff = 0.0;

    // ── Simulation with antithetic variates ─────────────────────────────
    int half = num_paths_ / 2;
    for (int i = 0; i < half; ++i) {
        double z = dist(gen);

        // Regular path
        double ST1 = S * std::exp(drift + diffusion * z);
        // Antithetic path
        double ST2 = S * std::exp(drift - diffusion * z);

        double payoff1, payoff2;
        if (option.option_type == OptionType::Call) {
            payoff1 = std::max(ST1 - K, 0.0);
            payoff2 = std::max(ST2 - K, 0.0);
        } else {
            payoff1 = std::max(K - ST1, 0.0);
            payoff2 = std::max(K - ST2, 0.0);
        }

        sum_payoff += payoff1 + payoff2;

        result.path_prices.push_back(ST1);
        result.path_prices.push_back(ST2);
    }

    // Handle odd number of paths
    if (num_paths_ % 2 != 0) {
        double z = dist(gen);
        double ST = S * std::exp(drift + diffusion * z);
        double payoff = (option.option_type == OptionType::Call)
                        ? std::max(ST - K, 0.0)
                        : std::max(K - ST, 0.0);
        sum_payoff += payoff;
        result.path_prices.push_back(ST);
    }

    result.price = discount * sum_payoff / num_paths_;

    return result;
}

}  // namespace quantiv::models
