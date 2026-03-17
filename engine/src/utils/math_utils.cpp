/**
 * @file math_utils.cpp
 * @brief Implementations of norm_cdf and norm_pdf.
 */

#include "quantiv/utils/math_utils.hpp"
#include "quantiv/utils/constants.hpp"

#include <cmath>

namespace quantiv::utils {

double norm_pdf(double x) {
    return INV_SQRT_2PI * std::exp(-0.5 * x * x);
}

double norm_cdf(double x) {
    // Abramowitz & Stegun approximation (rational, max error ~7.5e-8).
    if (x < -10.0) return 0.0;
    if (x >  10.0) return 1.0;

    return 0.5 * std::erfc(-x * std::sqrt(0.5));
}

}  // namespace quantiv::utils
