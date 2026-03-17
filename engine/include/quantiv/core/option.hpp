#pragma once

/**
 * @file option.hpp
 * @brief Core data structure representing an option contract.
 */

#include <string>

namespace quantiv::core {

/// Option type: Call or Put.
enum class OptionType {
    Call,
    Put
};

/// Exercise style.
enum class ExerciseStyle {
    European,
    American
};

/**
 * @brief Represents a vanilla option contract.
 */
struct Option {
    double        strike;          ///< Strike price (K)
    double        expiry;          ///< Time to expiration in years (T)
    OptionType    option_type;     ///< Call or Put
    ExerciseStyle exercise_style;  ///< European or American

    Option() = default;

    Option(double strike, double expiry,
           OptionType option_type,
           ExerciseStyle exercise_style = ExerciseStyle::European)
        : strike(strike)
        , expiry(expiry)
        , option_type(option_type)
        , exercise_style(exercise_style) {}
};

}  // namespace quantiv::core
