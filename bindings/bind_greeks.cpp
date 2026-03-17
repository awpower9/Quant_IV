/**
 * @file bind_greeks.cpp
 * @brief pybind11 bindings for the Greeks engine.
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "quantiv/greeks/greeks_engine.hpp"

namespace py = pybind11;
using quantiv::greeks::GreeksEngine;

void init_greeks_bindings(py::module_& m) {
    py::class_<GreeksEngine>(m, "GreeksEngine",
        "Option Greeks calculator")
        .def(py::init<>())
        .def("compute_bsm_greeks", &GreeksEngine::compute_bsm_greeks,
             py::arg("option"), py::arg("market"),
             "Compute analytical BSM Greeks")
        .def("compute_delta_fd", &GreeksEngine::compute_delta_fd,
             py::arg("option"), py::arg("market"), py::arg("bump") = 0.01)
        .def("compute_gamma_fd", &GreeksEngine::compute_gamma_fd,
             py::arg("option"), py::arg("market"), py::arg("bump") = 0.01)
        .def("compute_vega_fd", &GreeksEngine::compute_vega_fd,
             py::arg("option"), py::arg("market"), py::arg("bump") = 0.01)
        .def("compute_theta_fd", &GreeksEngine::compute_theta_fd,
             py::arg("option"), py::arg("market"),
             py::arg("bump") = 1.0 / 365.0)
        .def("compute_rho_fd", &GreeksEngine::compute_rho_fd,
             py::arg("option"), py::arg("market"), py::arg("bump") = 0.01);
}
