"""
greeks_callbacks.py — Callbacks for the Greeks dashboard page.
"""

import dash
from dash import Input, Output, State, dcc
import plotly.graph_objects as go

from quantiv.analytics import GreeksAnalyzer
from quantiv import _quantiv_engine # ---> NEW: C++ Engine

analyzer = GreeksAnalyzer()
engine = _quantiv_engine.QuantivPortfolioEngine()


@dash.callback(
    Output("greeks-chart", "figure"),
    Input("btn-calculate-greeks", "n_clicks"),   # Trigger 1
    Input("greeks-tabs", "active_tab"),          # Trigger 2 (Changing tabs re-calculates)
    State("greeks-spot", "value"),
    State("greeks-strike", "value"),
    State("greeks-vol", "value"),
    State("greeks-rate", "value"),
    State("greeks-expiry", "value"),
    State("greeks-option-type", "value"),
    State("session-user", "data"),               # ---> NEW: Session
)
def update_greeks_chart(n_clicks, active_tab, spot, strike, vol_pct, rate_pct, expiry, option_type, username):
    """Update the Greeks chart based on the selected tab and deduct credits."""
    
    fig = go.Figure()
    
    # 1. Prevent calculation on page load
    if n_clicks is None:
        fig.add_annotation(text="Click 'Calculate' to generate Greek chart.", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="#94a3b8"))
        fig.update_layout(template="plotly_dark", height=500, xaxis=dict(visible=False), yaxis=dict(visible=False))
        return fig

    # 2. Login Check
    if not username:
        fig.add_annotation(text="🔒 Please log in via the Portfolio tab to view charts.", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="#ff4f6d"))
        fig.update_layout(template="plotly_dark", height=500, xaxis=dict(visible=False), yaxis=dict(visible=False))
        return fig
        
    # 3. Credit Check
    if not engine.use_advanced_feature(username):
        fig.add_annotation(text="⚡ Out of credits! Please upgrade your plan to view charts.", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="#f5c542"))
        fig.update_layout(template="plotly_dark", height=500, xaxis=dict(visible=False), yaxis=dict(visible=False))
        return fig

    # 4. Generate Chart
    try:
        vol = vol_pct / 100.0
        rate = rate_pct / 100.0
        spot_min = max(spot * 0.5, 1.0)
        spot_max = spot * 1.5

        df = analyzer.greeks_vs_spot(
            spot_range=(spot_min, spot_max),
            strike=strike, vol=vol, rate=rate,
            expiry=expiry, option_type=option_type,
        )

        greek_name = active_tab.replace("-tab", "")

        if greek_name in df.columns:
            fig.add_trace(go.Scatter(
                x=df["spot"], y=df[greek_name],
                mode="lines", name=greek_name.capitalize(),
                line=dict(color="#00d4ff", width=2),
                fill="tozeroy", fillcolor="rgba(0, 212, 255, 0.1)",
            ))

            fig.add_vline(x=spot, line_dash="dash", line_color="yellow", annotation_text="Current Spot")

        fig.update_layout(
            title=f"{greek_name.capitalize()} vs Spot Price",
            xaxis_title="Spot Price ($)", yaxis_title=greek_name.capitalize(),
            template="plotly_dark", height=500,
        )
        return fig

    except Exception as e:
        fig.add_annotation(text=f"Error: {e}", showarrow=False)
        fig.update_layout(template="plotly_dark")
        return fig
