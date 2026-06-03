"""
comparison_page.py — Model Comparison page layout.
"""
import dash_bootstrap_components as dbc
from dash import html, dcc

def comparison_layout() -> html.Div:
    """Create the model comparison page layout."""
    return html.Div(className="container-fluid p-4 animate-page", children=[
        html.H2("Multi-Model Comparison Analysis", className="text-neon mb-4 fw-bold"),

        dbc.Row([
            # Left Column: Inputs (Aggregated Merton & Heston)
            dbc.Col(md=4, children=[
                html.Div(className="glass-card p-4", children=[
                    html.H5("Benchmark Parameters", className="mb-4 text-info fw-bold"),
                    
                    # 1. Base Market Parameters
                    html.Label("Spot Price: ", className="small"),
                    html.Span("100", id="comp-spot-value", className="fw-bold ms-1"),
                    dcc.Slider(id="comp-spot", min=50, max=200, value=100, step=1, marks=None, tooltip={"placement": "bottom"}),

                    html.Label("Strike Price: ", className="mt-2 small"),
                    html.Span("100", id="comp-strike-value", className="fw-bold ms-1"),
                    dcc.Slider(id="comp-strike", min=50, max=200, value=100, step=1, marks=None, tooltip={"placement": "bottom"}),

                    html.Label("Volatility (%): ", className="mt-2 small"),
                    html.Span("20", id="comp-vol-value", className="fw-bold ms-1"),
                    dcc.Slider(id="comp-vol", min=5, max=100, value=20, step=1, marks=None, tooltip={"placement": "bottom"}),

                    html.Label("Risk-Free Rate (%): ", className="mt-2 small"),
                    html.Span("5", id="comp-rate-value", className="fw-bold ms-1"),
                    dcc.Slider(id="comp-rate", min=0, max=20, value=5, step=0.5, marks=None, tooltip={"placement": "bottom"}),

                    html.Label("Time to Expiry (years): ", className="mt-2 small"),
                    html.Span("1.0", id="comp-expiry-value", className="fw-bold ms-1"),
                    dcc.Slider(id="comp-expiry", min=0.1, max=5.0, value=1.0, step=0.1, marks=None, tooltip={"placement": "bottom"}),

                    html.Label("Option Type", className="mt-3 small d-block"),
                    dbc.RadioItems(
                        id="comp-option-type",
                        options=[{"label": "Call", "value": "call"}, {"label": "Put", "value": "put"}],
                        value="call", inline=True, className="mb-4"
                    ),

                    # 2. Merton Jump Parameters
                    html.Hr(className="my-3"),
                    html.H6("⚙️ Merton Jump Parameters", className="text-warning fw-bold mb-3 small"),
                    
                    html.Label("λ (Expected Jumps/Year)", className="small"),
                    dcc.Slider(id="comp-merton-lambda", min=0, max=5, step=0.1, value=1.0, marks=None, tooltip={"placement": "bottom"}),

                    html.Label("μⱼ (Mean Jump Size)", className="mt-2 small"),
                    dcc.Slider(id="comp-merton-muj", min=-0.5, max=0.5, step=0.01, value=-0.15, marks=None, tooltip={"placement": "bottom"}),

                    html.Label("σⱼ (Jump Volatility)", className="mt-2 small"),
                    dcc.Slider(id="comp-merton-sigmaj", min=0.01, max=0.5, step=0.01, value=0.20, marks=None, tooltip={"placement": "bottom"}),

                    # 3. Heston Volatility Parameters
                    html.Hr(className="my-3"),
                    html.H6("⚙️ Heston Vol Parameters", className="text-warning fw-bold mb-3 small"),

                    html.Label("κ (Mean Reversion Speed)", className="small"),
                    dcc.Slider(id="comp-heston-kappa", min=0.1, max=5, step=0.1, value=2.0, marks=None, tooltip={"placement": "bottom"}),

                    html.Label("θ (Long-Term Variance)", className="mt-2 small"),
                    dcc.Slider(id="comp-heston-theta", min=0.01, max=0.5, step=0.01, value=0.04, marks=None, tooltip={"placement": "bottom"}),

                    html.Label("σᵥ (Vol of Volatility)", className="mt-2 small"),
                    dcc.Slider(id="comp-heston-sigma-v", min=0.01, max=1.0, step=0.01, value=0.3, marks=None, tooltip={"placement": "bottom"}),

                    html.Label("ρ (Price/Vol Correlation)", className="mt-2 small"),
                    dcc.Slider(id="comp-heston-rho", min=-1.0, max=1.0, step=0.05, value=-0.7, marks=None, tooltip={"placement": "bottom"}),

                    # 4. Binomial Tree Parameters
                    html.Hr(className="my-3"),
                    html.H6("⚙️ Binomial Tree Parameters", className="text-warning fw-bold mb-3 small"),

                    html.Label("Number of Steps", className="small"),
                    dcc.Slider(id="comp-binomial-steps", min=10, max=500, step=10, value=100, marks=None, tooltip={"placement": "bottom"}),

                    dbc.Button(
                        "🔍 Run Model Comparison", 
                        id="btn-run-comparison-page", 
                        className="btn-calculate w-100 mt-4 py-3"
                    )
                ])
            ]),

            # Right Column: Big Display & Charts
            dbc.Col(md=8, children=[
                # Results Table
                html.Div(className="glass-card p-4 mb-4", children=[
                    html.H5("COMPARISON SUMMARY", className="text-muted small", style={'letterSpacing': '3px'}),
                    html.Div(id="comp-table-output")
                ]),
                
                # Big Chart
                html.Div(className="glass-card p-4", children=[
                    html.H5("SENSITIVITY ANALYSIS: PRICE VS SPOT", className="text-muted small", style={'letterSpacing': '2px'}),
                    dcc.Graph(id="comp-chart-output", config={'displayModeBar': False})
                ])
            ])
        ])
    ])
