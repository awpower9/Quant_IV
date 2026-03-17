/**
 * @file binomial.cpp
 * @brief Cox-Ross-Rubinstein binomial tree pricing implementation.
 */

#include "quantiv/models/binomial.hpp"

#include <cmath>
#include <algorithm>
#include <vector>

namespace quantiv::models {

using namespace quantiv::core;

Binomial::Binomial(int steps) : steps_(steps) {}

PricingResult Binomial::price(const Option& option,
                              const MarketData& market) const {
    PricingResult result;

    double S     = market.spot;
    double K     = option.strike;
    double r     = market.rate;
    double q     = market.dividend;
    double sigma = market.vol;
    double T     = option.expiry;
    int    N     = steps_;

    double dt = T / N;
    double u  = std::exp(sigma * std::sqrt(dt));          // up factor
    double d  = 1.0 / u;                                  // down factor
    double p  = (std::exp((r - q) * dt) - d) / (u - d);  // risk-neutral prob
    double disc = std::exp(-r * dt);                       // per-step discount

    // ── Build terminal payoffs ──────────────────────────────────────────
    std::vector<double> prices(N + 1);
    for (int i = 0; i <= N; ++i) {
        double ST = S * std::pow(u, N - i) * std::pow(d, i);
        if (option.option_type == OptionType::Call)
            prices[i] = std::max(ST - K, 0.0);
        else
            prices[i] = std::max(K - ST, 0.0);
    }

    // Store the tree for visualization (optional; outer vector = time step)
    result.tree.resize(N + 1);
    result.tree[N] = prices;

    // ── Backward induction ──────────────────────────────────────────────
    for (int step = N - 1; step >= 0; --step) {
        std::vector<double> step_prices(step + 1);
        for (int i = 0; i <= step; ++i) {
            double hold = disc * (p * prices[i] + (1.0 - p) * prices[i + 1]);

            if (option.exercise_style == ExerciseStyle::American) {
                double ST = S * std::pow(u, step - i) * std::pow(d, i);
                double exercise = (option.option_type == OptionType::Call)
                                  ? std::max(ST - K, 0.0)
                                  : std::max(K - ST, 0.0);
                step_prices[i] = std::max(hold, exercise);
            } else {
                step_prices[i] = hold;
            }
        }
        prices = step_prices;
        result.tree[step] = step_prices;
    }

    result.price = prices[0];
    return result;
}

}  // namespace quantiv::models
