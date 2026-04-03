#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // Required to convert C++ std::vector/std::string to Python lists/strings

// Assuming you moved your portfolio header to the new include folder
#include "quantiv/core/portfolio_engine.h" 

namespace py = pybind11;

void init_portfolio_bindings(py::module_& m) {
    // Bind the Position struct
    py::class_<Position>(m, "Position")
        .def_readonly("symbol", &Position::symbol)
        .def_readonly("name", &Position::name)
        .def_readonly("quantity", &Position::quantity)
        .def_readonly("purchase_price", &Position::purchase_price)
        .def_readonly("current_total_value", &Position::current_total_value);

    // Bind the QuantivPortfolioEngine class
    py::class_<QuantivPortfolioEngine>(m, "QuantivPortfolioEngine")
        .def(py::init<>()) // Constructor
        .def("create_user", &QuantivPortfolioEngine::create_user)
        .def("authenticate_user", &QuantivPortfolioEngine::authenticate_user)
        .def("get_subscription_tier", &QuantivPortfolioEngine::get_subscription_tier)
        .def("get_available_cash", &QuantivPortfolioEngine::get_available_cash)
        .def("get_portfolio_value", &QuantivPortfolioEngine::get_portfolio_value)
        .def("get_user_portfolio", &QuantivPortfolioEngine::get_user_portfolio)
        .def("get_remaining_uses", &QuantivPortfolioEngine::get_remaining_uses)
        .def("upgrade_subscription", &QuantivPortfolioEngine::upgrade_subscription)
        .def("use_advanced_feature", &QuantivPortfolioEngine::use_advanced_feature)
        .def("buy_stock", &QuantivPortfolioEngine::buy_stock)
        .def("sell_stock", &QuantivPortfolioEngine::sell_stock)
        .def("buy_credit_bundle", &QuantivPortfolioEngine::buy_credit_bundle); 

}