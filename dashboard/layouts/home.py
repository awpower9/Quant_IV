"""
home.py — Modernized Home / Landing page with Glassmorphism and Bento Grid.
"""

import dash_bootstrap_components as dbc
from dash import html


def home_layout() -> html.Div:
    """Create the high-performance home page layout."""
    return html.Div(className="container-fluid p-5 animate-page", children=[
        # Hero Section
        dbc.Row([
            dbc.Col([
                html.H1("QUANTIV", className="hero-title fw-bold mb-0"),
                html.P(
                    "INTEGRATED QUANTITATIVE TERMINAL",
                    style={'letterSpacing': '8px', 'color': '#8b949e', 'fontSize': '0.9rem'}
                ),
                html.P(
                    "High-performance options engine powered by C++ and PostgreSQL.",
                    className="lead text-muted mt-4",
                ),
            ], md=12, className="text-center mb-5"),
        ]),

        # Bento Grid of Features
        dbc.Row([
            # Row 1
            _feature_card("Introduction", "Master the Greeks and Option math.", "/intro", "delay-1"),
            _feature_card("Multi-Model Pricer", "BSM, Trees, and Monte Carlo.", "/models", "delay-2"),
            _feature_card("Greeks Dashboard", "Real-time risk sensitivity analysis.", "/greeks", "delay-3"),
            _feature_card("Volatility Surface", "3D Implied Volatility mapping.", "/surface", "delay-4"),
            
            # Row 2 (Added Portfolio & Subscription)
            _feature_card("Strategy Builder", "Construct and stress-test legs.", "/strategy", "delay-5"),
            _feature_card(" Portfolio", "Track trades & manage your balance.", "/portfolio", "delay-6"),
            _feature_card("Subscription", "Upgrade credits for advanced visuals.", "/subscription", "delay-7"),
        ], className="g-4 justify-content-center"),
    ])


def _feature_card(title: str, description: str, href: str, delay_class: str) -> dbc.Col:
    """Create a Glassmorphic feature card with staggered animation."""
    return dbc.Col(
        html.A(href=href, style={"textDecoration": "none"}, children=[
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.H5(title, className="card-title text-neon mb-3"),
                        html.P(description, className="card-text text-muted small"),
                    ], style={"minHeight": "100px"}),
                    html.Div("ACCESS TERMINAL", className=" small fw-bold mt-3", style={"letterSpacing": "1px"})
                ]),
                # Combine glass style with staggered animation
                className=f"glass-cards h-100 bento-reveal {delay_class}",
            )
        ]),
        md=6, lg=3,
    )