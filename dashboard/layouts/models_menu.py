"""
models_menu.py — Multi-Model Pricer Selection Menu
"""

import dash_bootstrap_components as dbc
from dash import html

def _model_card(title: str, icon: str, description: str, bullets: list, href: str) -> dbc.Col:
    return dbc.Col(
        html.A(
            dbc.Card([
                html.Div(
                    html.H2(icon, className="mb-0 text-center text-white"),
                    style={
                        "backgroundColor": "#3b9b9b", 
                        "borderTopLeftRadius": "0.375rem", 
                        "borderTopRightRadius": "0.375rem", 
                        "padding": "1.5rem"
                    }
                ),
                dbc.CardBody([
                    html.H4(title, className="text-center font-weight-bold mt-2"),
                    html.Div(style={
                        "height": "3px", 
                        "width": "50px", 
                        "backgroundColor": "#3b9b9b", 
                        "margin": "10px auto"
                    }),
                    html.P(description, className="text-center text-muted mb-4", style={"fontSize": "0.95rem"}),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Span("● ", style={"color": "#3b9b9b", "fontSize": "0.8rem", "marginRight": "5px"}),
                            html.Span(bullet, style={"fontSize": "0.85rem"})
                        ], md=4, className="d-flex align-items-baseline mb-2")
                        for bullet in bullets
                    ], className="justify-content-center")
                ])
            ], className="shadow h-100 border-0", style={"transition": "transform 0.2s"}),
            href=href,
            className="text-decoration-none text-light"
        ),
        md=10, lg=10, className="mx-auto mb-4"
    )

def models_menu_layout() -> html.Div:
    """Create the model selection page layout."""
    return html.Div([
        dbc.Container([
            html.H2("Multi-Model Pricer Selection", className="text-neon text-center mb-5 mt-3"),
            
            dbc.Row([
                _model_card(
                    "Black-Scholes Model",
                    "📈",
                    "Analytical closed-form solution for European options pricing.",
                    ["Fastest execution", "Assumes log-normal distribution", "Constant volatility"],
                    "/pricer?model=bsm"
                ),
                _model_card(
                    "Binomial Tree",
                    "🌳",
                    "Cox-Ross-Rubinstein binomial tree for American & European options.",
                    ["Handles early exercise", "Discrete time steps", "Visual convergence"],
                    "/pricer?model=binomial"
                ),
                _model_card(
                    "Trinomial Tree",
                    "🌲",
                    "Three-branch lattice model for increased pricing accuracy.",
                    ["Faster convergence", "Stable Greeks calculation", "Complex payoffs"],
                    "/pricer?model=trinomial"
                ),
                _model_card(
                    "Monte Carlo Simulation",
                    "🎲",
                    "Stochastic simulation with Geometric Brownian Motion paths.",
                    ["Path-dependent options", "Highly customizable", "Computationally intensive"],
                    "/pricer?model=monte_carlo"
                ),
                _model_card(
                    "Heston Model (Only for Pro Users)",
                    "🌪️",
                    "Stochastic volatility model with mean-reverting variance dynamics.",
                    ["Volatility smile", "Correlated processes", "Characteristic function"],
                    "/pricer?model=heston"
                ),
                _model_card(
                    "Merton Jump-Diffusion (Only for Pro Users)",
                    "🦢",
                    "Jump-diffusion model capturing Black Swan crash events.",
                    ["Fat tail pricing", "Poisson jump process", "Crash risk modeling"],
                    "/pricer?model=merton"
                ),
            ])
        ], className="py-4")
    ])
