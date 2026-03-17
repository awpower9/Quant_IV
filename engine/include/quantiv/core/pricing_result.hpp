#pragma once

/**
 * @file pricing_result.hpp
 * @brief Pricing result container returned by all models.
 */

#include <map>
#include <string>
#include <vector>

namespace quantiv::core {

/**
 * @brief Contains the output of a pricing computation.
 */
struct PricingResult {
    double price = 0.0;                       ///< Theoretical option price
    std::map<std::string, double> greeks;      ///< Named Greeks (delta, gamma, ...)
    std::vector<std::vector<double>> tree;     ///< Tree node values (for lattice models)
    std::vector<double> path_prices;           ///< Simulated terminal prices (for MC)

    PricingResult() = default;
    explicit PricingResult(double price) : price(price) {}
};

}  // namespace quantiv::core
