/**
 * @file bind_binomial.cpp
 * @brief pybind11 bindings for the Binomial tree model.
 */

#include <pybind11/pybind11.h>
#include "quantiv/models/binomial.hpp"

namespace py = pybind11;
using quantiv::models::Binomial;

void init_binomial_bindings(py::module_& m) {
    py::class_<Binomial>(m, "Binomial",
        "Cox-Ross-Rubinstein binomial tree pricer")
        .def(py::init<int>(), py::arg("steps") = 100)
        .def("price", &Binomial::price,
             py::arg("option"), py::arg("market"))
        .def_property("steps", &Binomial::steps, &Binomial::set_steps);
}
