"""
comparison_callbacks.py — Callbacks for the dedicated model comparison page.
"""
import dash
from dash import html, dcc, Input, Output, State
import plotly.graph_objects as go
import numpy as np

from quantiv.portfolio_engine import QuantivPortfolioEngine
from dashboard.grpc_client import QuantivGrpcClient
from quantiv.utils.formatting import format_price

# Initialize common engines
engine_core = QuantivPortfolioEngine()
grpc_client = QuantivGrpcClient()


# ══════════════════════════════════════════════════════════════════════════════
# 1. PARAMETER DISPLAY SYNC
# ══════════════════════════════════════════════════════════════════════════════

# Sync slider values with labels for standard parameters
@dash.callback(
    [Output(f"comp-{p}-value", "children") for p in ["spot", "strike", "vol", "rate", "expiry"]],
    [Input(f"comp-{p}", "value") for p in ["spot", "strike", "vol", "rate", "expiry"]]
)
def sync_comp_labels(spot, strike, vol, rate, expiry):
    return [str(spot), str(strike), str(vol), str(rate), f"{expiry:.1f}"]


# ══════════════════════════════════════════════════════════════════════════════
# 2. MASTER COMPARISON CALLBACK
# ══════════════════════════════════════════════════════════════════════════════

@dash.callback(
    Output("comp-table-output", "children"),
    Output("comp-chart-output", "figure"),
    Input("btn-run-comparison-page", "n_clicks"),
    State("comp-spot", "value"),
    State("comp-strike", "value"),
    State("comp-vol", "value"),
    State("comp-rate", "value"),
    State("comp-expiry", "value"),
    State("comp-option-type", "value"),
    # Merton
    State("comp-merton-lambda", "value"),
    State("comp-merton-muj", "value"),
    State("comp-merton-sigmaj", "value"),
    # Heston
    State("comp-heston-kappa", "value"),
    State("comp-heston-theta", "value"),
    State("comp-heston-sigma-v", "value"),
    State("comp-heston-rho", "value"),
    # Binomial
    State("comp-binomial-steps", "value"),
    State("session-user", "data"),
)
def update_comparison_dashboard(n_clicks, spot, strike, vol_pct, rate_pct, expiry, option_type, 
                                m_lambda, m_muj, m_sigmaj,
                                h_kappa, h_theta, h_sigmav, h_rho,
                                b_steps,
                                username):
    """Executes all three models and generates a benchmark dashboard."""
    
    if not n_clicks:
        fig = go.Figure()
        fig.update_layout(template="plotly_dark", height=400, xaxis=dict(visible=False), yaxis=dict(visible=False))
        return html.P("Adjust parameters and click 'Run Model Comparison' to begin analysis.", className="text-muted"), fig

    try:
        # Extract and Validate Parameters
        vol = vol_pct / 100.0
        rate = rate_pct / 100.0
        is_call = option_type.lower() == "call"

        
        # 1. Current Spot Pricing
        bsm_res = grpc_client.price_black_scholes(spot, strike, vol, rate, expiry, is_call)
        merton_res = grpc_client.price_merton(spot, strike, vol, rate, expiry, is_call, m_lambda, m_muj, m_sigmaj)
        heston_res = grpc_client.price_heston(spot, strike, vol, rate, expiry, is_call, h_kappa, h_theta, h_sigmav, h_rho)
        bin_res = grpc_client.price_binomial(spot, strike, vol, rate, expiry, is_call, b_steps)

        # 2. Sensitivity Analysis (Spot Sweep)
        spot_range = np.linspace(spot * 0.7, spot * 1.3, 50)
        p_bsm, p_merton, p_heston, p_bin = [], [], [], []

        for s in spot_range:
            p_bsm.append(grpc_client.price_black_scholes(s, strike, vol, rate, expiry, is_call).price)
            p_merton.append(grpc_client.price_merton(s, strike, vol, rate, expiry, is_call, m_lambda, m_muj, m_sigmaj).price)
            p_heston.append(grpc_client.price_heston(s, strike, vol, rate, expiry, is_call, h_kappa, h_theta, h_sigmav, h_rho).price)
            p_bin.append(grpc_client.price_binomial(s, strike, vol, rate, expiry, is_call, b_steps).price)

        # 3. Build Comparison Table
        def get_diff(p1, base):
            if base == 0: return "N/A"
            diff = ((p1 - base) / base) * 100
            color = "text-success" if diff >= 0 else "text-danger"
            return html.Span(f"{diff:+.2f}%", className=color)

        table = html.Table([
            html.Thead(html.Tr([
                html.Th("Model"), html.Th("Theoretical Price"), html.Th("Delta (Δ)"), html.Th("Gamma (Γ)"), html.Th("% Diff (vs BSM)")
            ])),
            html.Tbody([
                html.Tr([
                    html.Td("Black-Scholes (Baseline)"), 
                    html.Td(format_price(bsm_res.price)), 
                    html.Td(f"{bsm_res.greeks.delta:.4f}" if bsm_res.HasField("greeks") else "0.0"),
                    html.Td(f"{bsm_res.greeks.gamma:.4f}" if bsm_res.HasField("greeks") else "0.0"),
                    html.Td("—", className="text-muted")
                ]),
                html.Tr([
                    html.Td("Merton Jump-Diffusion"), 
                    html.Td(format_price(merton_res.price)), 
                    html.Td(f"{merton_res.greeks.delta:.4f}" if merton_res.HasField("greeks") else "0.0"),
                    html.Td(f"{merton_res.greeks.gamma:.4f}" if merton_res.HasField("greeks") else "0.0"),
                    html.Td(get_diff(merton_res.price, bsm_res.price))
                ]),
                html.Tr([
                    html.Td("Heston Stochastic Vol"), 
                    html.Td(format_price(heston_res.price)), 
                    html.Td(f"{heston_res.greeks.delta:.4f}" if heston_res.HasField("greeks") else "0.0"),
                    html.Td(f"{heston_res.greeks.gamma:.4f}" if heston_res.HasField("greeks") else "0.0"),
                    html.Td(get_diff(heston_res.price, bsm_res.price))
                ]),
                html.Tr([
                    html.Td(f"Binomial Tree ({b_steps} steps)"), 
                    html.Td(format_price(bin_res.price)), 
                    html.Td(f"{bin_res.greeks.delta:.4f}" if bin_res.HasField("greeks") else "0.0"),
                    html.Td(f"{bin_res.greeks.gamma:.4f}" if bin_res.HasField("greeks") else "0.0"),
                    html.Td(get_diff(bin_res.price, bsm_res.price))
                ]),
            ])
        ], className="table table-dark table-hover mb-0")

        # 4. Build Sensitivity Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=spot_range, y=p_bsm, name="Black-Scholes", line=dict(color="#94a3b8", dash="dash")))
        fig.add_trace(go.Scatter(x=spot_range, y=p_merton, name="Merton Jump", line=dict(color="#a855f7", width=3)))
        fig.add_trace(go.Scatter(x=spot_range, y=p_heston, name="Heston Stochastic Vol", line=dict(color="#00d4ff", width=3)))
        fig.add_trace(go.Scatter(x=spot_range, y=p_bin, name="Binomial Tree", line=dict(color="#22c55e", width=2, dash="dot")))
        
        fig.add_vline(x=spot, line_dash="dot", line_color="white", annotation_text="Current")
        fig.add_vline(x=strike, line_dash="dot", line_color="yellow", annotation_text="ATM")

        fig.update_layout(
            template="plotly_dark",
            margin=dict(l=20, r=20, t=40, b=20),
            height=450,
            xaxis_title="Underlying Price (₹)",
            yaxis_title="Option Price (₹)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        return table, fig

    except Exception as e:
        return html.Div(f"Computation Error: {e}", className="text-danger"), go.Figure()
