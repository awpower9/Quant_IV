import sys
code = '''from quantiv.data.providers.yahoo import YahooFinanceProvider
from scripts.calculate_iv import implied_volatility_educational
import json
import datetime
import plotly.graph_objects as go
import dash

@dash.callback(
    Output("live-chain-store", "data"),
    Output("live-chain-container", "style"),
    Output("live-chain-status", "children"),
    Output("pricer-chain-expiry", "options"),
    Output("pricer-chain-expiry", "value"),
    Input("btn-fetch-chain", "n_clicks"),
    State("pricer-ticker-input", "value"),
    prevent_initial_call=True
)
def fetch_live_chain_standalone(n_clicks, ticker):
    if not ticker:
        return dash.no_update, {"display": "none"}, "Please enter a ticker.", [], None
    try:
        provider = YahooFinanceProvider()
        spot = provider.get_spot_price(ticker)
        chain = provider.get_option_chain(ticker)
        rate = provider.get_risk_free_rate()
        expiries = sorted(list(set([c.expiry for c in chain.contracts])))
        now = datetime.datetime.now()
        expiry_opts = [{"label": f"{(now + datetime.timedelta(days=e*365.25)).strftime('%b %d, %Y')} ({e:.3f}y)", "value": e} for e in expiries]
        chain_data = {
            "spot": spot,
            "rate": rate,
            "contracts": [{"strike": c.strike, "expiry": c.expiry, "option_type": c.option_type, "last": c.last} for c in chain.contracts]
        }
        return json.dumps(chain_data), {"display": "block"}, f"Fetched {len(chain.contracts)} contracts for {ticker.upper()}.", expiry_opts, expiries[0] if expiries else None
    except Exception as e:
        return dash.no_update, {"display": "none"}, f"Error: {e}", [], None

@dash.callback(
    Output("pricer-chain-strike", "options"),
    Output("pricer-chain-strike", "value"),
    Input("pricer-chain-expiry", "value"),
    Input("live-option-type", "value"),
    State("live-chain-store", "data"),
    prevent_initial_call=True
)
def update_strikes_standalone(expiry, option_type, chain_json):
    if not expiry or not chain_json:
        return [], None
    chain_data = json.loads(chain_json)
    strikes = sorted([c["strike"] for c in chain_data["contracts"] if c["expiry"] == expiry and c["option_type"] == option_type])
    opts = [{"label": f"${s:.2f}", "value": s} for s in strikes]
    return opts, strikes[len(strikes)//2] if strikes else None

@dash.callback(
    Output("pricer-convergence-chart", "figure", allow_duplicate=True),
    Output("live-chain-market-price", "children"),
    Output("live-chain-implied-vol", "children"),
    Input("pricer-chain-strike", "value"),
    State("pricer-chain-expiry", "value"),
    State("live-chain-store", "data"),
    State("live-option-type", "value"),
    prevent_initial_call=True
)
def calculate_iv_standalone(strike, expiry, chain_json, option_type):
    if not strike or not expiry or not chain_json:
        return dash.no_update, dash.no_update, dash.no_update
    data = json.loads(chain_json)
    contract = next((c for c in data["contracts"] if c["strike"] == strike and c["expiry"] == expiry and c["option_type"] == option_type), None)
    if not contract or contract["last"] <= 0:
        fig = go.Figure()
        fig.add_annotation(text="No valid market price to calculate IV.", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(template="plotly_dark", height=400, xaxis=dict(visible=False), yaxis=dict(visible=False))
        return fig, "Market Price: N/A", ""
    target_price = contract["last"]
    spot = data["spot"]
    rate = data["rate"]
    is_call = (option_type == "call")
    try:
        iv, steps = implied_volatility_educational(target_price, spot, strike, expiry, rate, is_call)
        iterations = [s["iteration"] for s in steps]
        vols = [s["sigma"] for s in steps]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=iterations, y=vols, mode="lines+markers", name="Volatility Guess", line=dict(color="#00d4ff")))
        fig.add_hline(y=iv, line_dash="dash", line_color="yellow", annotation_text=f"Converged IV: {iv:.2%}")
        fig.update_layout(title=f"Newton-Raphson IV Convergence (Target Price: ${target_price:.2f})", xaxis_title="Iteration Step", yaxis_title="Volatility Guess (σ)", template="plotly_dark", height=400)
        return fig, f"Market Price: ${target_price:.2f}", f"Converged Implied Vol: {iv:.2%}"
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"IV Error: {str(e)}", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(template="plotly_dark", height=400, xaxis=dict(visible=False), yaxis=dict(visible=False))
        return fig, f"Market Price: ${target_price:.2f}", ""
'''
with open('dashboard/callbacks/live_callbacks.py', 'a', encoding='utf-8') as f:
    f.write(code)
