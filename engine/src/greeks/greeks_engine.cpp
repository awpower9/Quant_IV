/**
 * @file greeks_engine.cpp
 * @brief Greeks calculation using analytical (BSM) and finite-difference methods.
 */

#include "quantiv/greeks/greeks_engine.hpp"
#include "quantiv/models/black_scholes.hpp"

#include <cmath>
#include <map>
#include <string>

namespace quantiv::greeks {

using namespace quantiv::core;

std::map<std::string, double> GreeksEngine::compute_bsm_greeks(
    const Option& option, const MarketData& market) const {
    // Delegate to BSM model which computes analytical Greeks.
    models::BlackScholes bsm;
    auto result = bsm.price(option, market);
    return result.greeks;
}

double GreeksEngine::compute_delta_fd(const Option& option,
                                      const MarketData& market,
                                      double bump) const {
    models::BlackScholes bsm;
    double abs_bump = market.spot * bump;

    MarketData up = market;   up.spot   = market.spot + abs_bump;
    MarketData down = market; down.spot = market.spot - abs_bump;

    double price_up   = bsm.price(option, up).price;
    double price_down = bsm.price(option, down).price;

    return (price_up - price_down) / (2.0 * abs_bump);
}

double GreeksEngine::compute_gamma_fd(const Option& option,
                                      const MarketData& market,
                                      double bump) const {
    models::BlackScholes bsm;
    double abs_bump = market.spot * bump;

    MarketData up = market;   up.spot   = market.spot + abs_bump;
    MarketData down = market; down.spot = market.spot - abs_bump;

    double price_up   = bsm.price(option, up).price;
    double price_mid  = bsm.price(option, market).price;
    double price_down = bsm.price(option, down).price;

    return (price_up - 2.0 * price_mid + price_down) / (abs_bump * abs_bump);
}

double GreeksEngine::compute_vega_fd(const Option& option,
                                     const MarketData& market,
                                     double bump) const {
    models::BlackScholes bsm;

    MarketData up = market;   up.vol  = market.vol + bump;
    MarketData down = market; down.vol = market.vol - bump;

    double price_up   = bsm.price(option, up).price;
    double price_down = bsm.price(option, down).price;

    return (price_up - price_down) / (2.0 * bump) / 100.0;  // per 1%
}

double GreeksEngine::compute_theta_fd(const Option& option,
                                      const MarketData& market,
                                      double bump) const {
    models::BlackScholes bsm;

    Option opt_later = option;
    opt_later.expiry = option.expiry - bump;
    if (opt_later.expiry < 0.0) opt_later.expiry = 0.0;

    double price_now  = bsm.price(option, market).price;
    double price_later = bsm.price(opt_later, market).price;

    return (price_later - price_now) / bump;  // negative = time decay
}

double GreeksEngine::compute_rho_fd(const Option& option,
                                    const MarketData& market,
                                    double bump) const {
    models::BlackScholes bsm;

    MarketData up = market;   up.rate  = market.rate + bump;
    MarketData down = market; down.rate = market.rate - bump;

    double price_up   = bsm.price(option, up).price;
    double price_down = bsm.price(option, down).price;

    return (price_up - price_down) / (2.0 * bump) / 100.0;  // per 1%
}

}  // namespace quantiv::greeks
