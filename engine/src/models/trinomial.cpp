/**
 * @file trinomial.cpp
 * @brief Trinomial tree pricing implementation.
 */

#include "quantiv/models/trinomial.hpp"

#include <cmath>
#include <algorithm>
#include <vector>

namespace quantiv::models {

using namespace quantiv::core;

Trinomial::Trinomial(int steps) : steps_(steps) {}

PricingResult Trinomial::price(const Option& option,
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
    double u  = std::exp(sigma * std::sqrt(2.0 * dt));     // up factor
    double d  = 1.0 / u;                                   // down factor
    double m  = 1.0;                                       // middle factor (no move)

    double drift = std::exp((r - q) * dt * 0.5);
    double pu = std::pow((drift - std::sqrt(d)) / (std::sqrt(u) - std::sqrt(d)), 2);
    double pd = std::pow((std::sqrt(u) - drift) / (std::sqrt(u) - std::sqrt(d)), 2);
    double pm = 1.0 - pu - pd;

    double disc = std::exp(-r * dt);

    // ── Terminal payoffs: 2N+1 nodes at final step ──────────────────────
    int terminal_nodes = 2 * N + 1;
    std::vector<double> prices(terminal_nodes);
    for (int i = 0; i < terminal_nodes; ++i) {
        double ST = S * std::pow(u, N - i);  // from top to bottom
        if (option.option_type == OptionType::Call)
            prices[i] = std::max(ST - K, 0.0);
        else
            prices[i] = std::max(K - ST, 0.0);
    }

    result.tree.resize(N + 1);
    result.tree[N] = prices;

    // ── Backward induction ──────────────────────────────────────────────
    for (int step = N - 1; step >= 0; --step) {
        int nodes = 2 * step + 1;
        std::vector<double> step_prices(nodes);
        for (int i = 0; i < nodes; ++i) {
            double hold = disc * (pu * prices[i] + pm * prices[i + 1]
                                  + pd * prices[i + 2]);

            if (option.exercise_style == ExerciseStyle::American) {
                double ST = S * std::pow(u, step - i);
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
