#pragma once

/**
 * @file math_utils.hpp
 * @brief Numerical utility functions: CDF, PDF, random number generation.
 */

namespace quantiv::utils {

/// Standard normal cumulative distribution function Φ(x).
double norm_cdf(double x);

/// Standard normal probability density function φ(x).
double norm_pdf(double x);

}  // namespace quantiv::utils
