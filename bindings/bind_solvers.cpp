/**
 * @file bind_solvers.cpp
 * @brief pybind11 bindings for the implied volatility solver.
 */

#include <pybind11/pybind11.h>
#include "quantiv/solvers/implied_vol.hpp"

namespace py = pybind11;
using quantiv::solvers::ImpliedVolSolver;

void init_solver_bindings(py::module_& m) {
    py::class_<ImpliedVolSolver>(m, "ImpliedVolSolver",
        "Newton-Raphson implied volatility solver")
        .def(py::init<double, int>(),
             py::arg("tol") = 1e-8,
             py::arg("max_iter") = 100)
        .def("solve", &ImpliedVolSolver::solve,
             py::arg("option"), py::arg("market"), py::arg("target_price"),
             "Solve for implied volatility given a market price");
}
