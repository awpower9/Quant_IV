/**
 * @file bind_trinomial.cpp
 * @brief pybind11 bindings for the Trinomial tree model.
 */

#include <pybind11/pybind11.h>
#include "quantiv/models/trinomial.hpp"

namespace py = pybind11;
using quantiv::models::Trinomial;

void init_trinomial_bindings(py::module_& m) {
    py::class_<Trinomial>(m, "Trinomial",
        "Trinomial tree pricer")
        .def(py::init<int>(), py::arg("steps") = 100)
        .def("price", &Trinomial::price,
             py::arg("option"), py::arg("market"))
        .def_property("steps", &Trinomial::steps, &Trinomial::set_steps);
}
