"""
pricer_page.py — Model pricing page layout.
"""
import dash_bootstrap_components as dbc
from dash import html, dcc
from dashboard.components.parameter_panel import create_parameter_panel
def pricer_layout(model: str = "bsm") -> html.Div:
    return html.Div(className="container-fluid p-4 animate-page", children=[
        dcc.Store(id="pricer-chain-store"),
        html.H2("Options Pricing Terminal", className="text-neon mb-4 fw-bold"),

        dbc.Row([
            # Left Column: Inputs
            dbc.Col(md=4, children=[
                # ── Market Parameters ──
                html.Div(className="glass-card p-4", children=[
                    html.H5("Market Parameters", className="mb-4 text-muted"),
                    create_parameter_panel(id_prefix="pricer", default_model=model),
                    dbc.Button(
                        "⚡ Run Models", 
                        id="btn-calculate-pricer", 
                        className="btn-calculate w-100 mt-4 py-3"
                    )
                ])
            ]),

            # Right Column: Big Display & Charts
            dbc.Col(md=8, children=[
                # Big Price Display
                html.Div(className="glass-card p-5 text-center mb-4", children=[
                    html.H5("THEORETICAL PRICE", className="text-muted small", style={'letterSpacing': '3px'}),
                    html.H1(id="pricer-price-output", className="display-1 fw-bold text-success")
                ]),
                
                # Bento Grid for Greeks and Chart
                dbc.Row([
                    dbc.Col(md=5, children=[
                        html.Div(className="glass-card p-4 h-100", children=[
                            html.H6("THE GREEKS", className="mb-3 text-muted"),
                            # --- THIS WAS THE MISSING ID ---
                            html.Div(id="pricer-greeks-output") 
                        ])
                    ]),
                    dbc.Col(md=7, children=[
                        html.Div(className="glass-card p-4 h-100", children=[
                            html.H6("MODEL CONVERGENCE", className="mb-3 text-muted"),
                            dcc.Graph(id="pricer-convergence-chart", config={'displayModeBar': False})
                        ])
                    ])
                ])
            ])
        ]),

        # ── Model Description / Educational Content ──
        html.Hr(className="my-4"),
        dbc.Row([
            dbc.Col(md=12, children=[
                html.Div(className="glass-card p-4", children=[
                    html.Div(id="model-description-output")
                ])
            ])
        ])
    ])