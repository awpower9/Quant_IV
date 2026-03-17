/**
 * @file module.cpp
 * @brief Top-level pybind11 module definition for _quantiv_engine.
 *
 * Each bind_*.cpp file provides an init_*() function that registers
 * its types/functions into the module.
 */

#include <pybind11/pybind11.h>

namespace py = pybind11;

// Forward declarations of sub-module initializers
void init_option_bindings(py::module_& m);
void init_black_scholes_bindings(py::module_& m);
void init_binomial_bindings(py::module_& m);
void init_trinomial_bindings(py::module_& m);
void init_monte_carlo_bindings(py::module_& m);
void init_greeks_bindings(py::module_& m);
void init_solver_bindings(py::module_& m);

PYBIND11_MODULE(_quantiv_engine, m) {
    m.doc() = "Quantiv C++ Options Pricing Engine";

    init_option_bindings(m);
    init_black_scholes_bindings(m);
    init_binomial_bindings(m);
    init_trinomial_bindings(m);
    init_monte_carlo_bindings(m);
    init_greeks_bindings(m);
    init_solver_bindings(m);
}
