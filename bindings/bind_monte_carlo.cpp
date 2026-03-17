/**
 * @file bind_monte_carlo.cpp
 * @brief pybind11 bindings for the Monte Carlo model.
 */

#include <pybind11/pybind11.h>
#include "quantiv/models/monte_carlo.hpp"

namespace py = pybind11;
using quantiv::models::MonteCarlo;

void init_monte_carlo_bindings(py::module_& m) {
    py::class_<MonteCarlo>(m, "MonteCarlo",
        "Monte Carlo simulation pricer")
        .def(py::init<int, unsigned int>(),
             py::arg("num_paths") = 100000,
             py::arg("seed") = 42)
        .def("price", &MonteCarlo::price,
             py::arg("option"), py::arg("market"))
        .def_property("num_paths", &MonteCarlo::num_paths, &MonteCarlo::set_num_paths)
        .def_property("seed", &MonteCarlo::seed, &MonteCarlo::set_seed);
}
