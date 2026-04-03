/**
 * @file bind_pro_engine.cpp
 * @brief pybind11 bindings for the ProEngine model.
 */

#include <pybind11/pybind11.h>
#include "quantiv/models/pro_engine.hpp"

namespace py = pybind11;
using quantiv::models::ProEngine;

void init_pro_engine_bindings(py::module_& m) {
    py::class_<ProEngine>(m, "ProEngine",
        "Advanced Pricing Engine for Jump-Diffusion and Stochastic Volatility")
        .def(py::init<>())
        .def("price_merton", &ProEngine::price_merton,
             py::arg("option"), py::arg("market"),
             py::arg("lamb"), py::arg("mu_j"), py::arg("sigma_j"),
             "Price an option using the Merton Jump-Diffusion model")
        .def("price_heston", &ProEngine::price_heston,
             py::arg("option"), py::arg("market"),
             py::arg("kappa"), py::arg("theta"), py::arg("vol_of_vol"), py::arg("rho"),
             "Price an option using the Heston Stochastic Volatility model");
}
