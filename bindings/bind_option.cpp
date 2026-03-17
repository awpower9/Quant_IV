/**
 * @file bind_option.cpp
 * @brief pybind11 bindings for Option, MarketData, and PricingResult.
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "quantiv/core/option.hpp"
#include "quantiv/core/market_data.hpp"
#include "quantiv/core/pricing_result.hpp"

namespace py = pybind11;

using namespace quantiv::core;

void init_option_bindings(py::module_& m) {
    // ── OptionType enum ─────────────────────────────────────────────────
    py::enum_<OptionType>(m, "OptionType")
        .value("Call", OptionType::Call)
        .value("Put", OptionType::Put)
        .export_values();

    // ── ExerciseStyle enum ──────────────────────────────────────────────
    py::enum_<ExerciseStyle>(m, "ExerciseStyle")
        .value("European", ExerciseStyle::European)
        .value("American", ExerciseStyle::American)
        .export_values();

    // ── Option ──────────────────────────────────────────────────────────
    py::class_<Option>(m, "Option", "Vanilla option contract")
        .def(py::init<double, double, OptionType, ExerciseStyle>(),
             py::arg("strike"),
             py::arg("expiry"),
             py::arg("option_type"),
             py::arg("exercise_style") = ExerciseStyle::European)
        .def_readwrite("strike", &Option::strike)
        .def_readwrite("expiry", &Option::expiry)
        .def_readwrite("option_type", &Option::option_type)
        .def_readwrite("exercise_style", &Option::exercise_style)
        .def("__repr__", [](const Option& o) {
            return "<Option strike=" + std::to_string(o.strike)
                 + " expiry=" + std::to_string(o.expiry)
                 + " type=" + (o.option_type == OptionType::Call ? "Call" : "Put")
                 + ">";
        });

    // ── MarketData ──────────────────────────────────────────────────────
    py::class_<MarketData>(m, "MarketData", "Market observable inputs")
        .def(py::init<double, double, double, double>(),
             py::arg("spot"),
             py::arg("vol"),
             py::arg("rate"),
             py::arg("dividend") = 0.0)
        .def_readwrite("spot", &MarketData::spot)
        .def_readwrite("vol", &MarketData::vol)
        .def_readwrite("rate", &MarketData::rate)
        .def_readwrite("dividend", &MarketData::dividend)
        .def("__repr__", [](const MarketData& md) {
            return "<MarketData spot=" + std::to_string(md.spot)
                 + " vol=" + std::to_string(md.vol)
                 + " rate=" + std::to_string(md.rate) + ">";
        });

    // ── PricingResult ───────────────────────────────────────────────────
    py::class_<PricingResult>(m, "PricingResult", "Output of a pricing computation")
        .def(py::init<>())
        .def_readwrite("price", &PricingResult::price)
        .def_readwrite("greeks", &PricingResult::greeks)
        .def_readwrite("tree", &PricingResult::tree)
        .def_readwrite("path_prices", &PricingResult::path_prices)
        .def("__repr__", [](const PricingResult& r) {
            return "<PricingResult price=" + std::to_string(r.price) + ">";
        });
}
