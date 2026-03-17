"""
home.py — Home / landing page layout.
"""

import dash_bootstrap_components as dbc
from dash import html


def home_layout() -> html.Div:
    """Create the home page layout."""
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("⚡ Quantiv", className="display-3 fw-bold"),
                    html.P(
                        "High-performance options pricing powered by C++",
                        className="lead text-muted",
                    ),
                    html.Hr(className="my-4"),
                    html.P(
                        "Price options using Black-Scholes, Binomial Trees, "
                        "Trinomial Trees, and Monte Carlo simulation — all backed "
                        "by a compiled C++ engine for maximum speed."
                    ),
                ], md=8, className="mx-auto text-center"),
            ], className="my-5"),

            dbc.Row([
                _feature_card(
                    "📖 Introduction",
                    "New to Options? Learn key concepts like Spot, Strike, Expiry, Volatility, and Moneyness before you build your strategies.",
                    "/intro",
                ),
                _feature_card(
                    "📊 Multi-Model Pricer",
                    "Compare BSM, Binomial, Trinomial, and Monte Carlo "
                    "pricing side by side.",
                    "/models",
                ),
                _feature_card(
                    "📈 Greeks Dashboard",
                    "Visualize Delta, Gamma, Vega, Theta, and Rho "
                    "across spot prices and time.",
                    "/greeks",
                ),
                _feature_card(
                    "🌐 Volatility Surface",
                    "Build 3D implied volatility surfaces across "
                    "strikes and maturities.",
                    "/surface",
                ),
                _feature_card(
                    "🎯 Strategy Builder",
                    "Construct multi-leg option strategies and "
                    "analyze P&L profiles.",
                    "/strategy",
                ),
            ], className="g-4"),
        ], className="py-4"),
    ])


def _feature_card(title: str, description: str, href: str) -> dbc.Col:
    """Create a feature card for the home page."""
    return dbc.Col(
        dbc.Card(
            dbc.CardBody([
                html.H5(title, className="card-title"),
                html.P(description, className="card-text text-muted"),
                dbc.Button("Explore →", href=href, color="primary", size="sm"),
            ]),
            className="shadow-sm h-100",
        ),
        md=6, lg=3,
    )
