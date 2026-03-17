/**
 * @file bind_black_scholes.cpp
 * @brief pybind11 bindings for the Black-Scholes model.
 */

#include <pybind11/pybind11.h>
#include "quantiv/models/black_scholes.hpp"

namespace py = pybind11;
using quantiv::models::BlackScholes;

void init_black_scholes_bindings(py::module_& m) {
    py::class_<BlackScholes>(m, "BlackScholes",
        "Black-Scholes-Merton analytical pricer")
        .def(py::init<>())
        .def("price", &BlackScholes::price,
             py::arg("option"), py::arg("market"),
             "Price an option using the BSM closed-form solution");
}
