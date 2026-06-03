"""
greeks_callbacks.py — Callbacks for the Greeks dashboard page.
"""

import dash
from dash import Input, Output, State, dcc
import plotly.graph_objects as go

from quantiv.analytics import GreeksAnalyzer
from quantiv.portfolio_engine import QuantivPortfolioEngine

analyzer = GreeksAnalyzer()
engine = QuantivPortfolioEngine()


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


# ══════════════════════════════════════════════════════════════════════════════
# GREEK DESCRIPTIONS
# ══════════════════════════════════════════════════════════════════════════════

GREEK_DESCRIPTIONS = {
    "delta": r'''
### 🏎️ Delta ($\Delta$) — The Speedometer

Tells you exactly how much the option price will theoretically change if the underlying stock moves by precisely **$1.00**. 

* **Intuition:** If you own an option with a Delta of 0.50, and the stock magically jumps up by $1 in the blink of an eye, your option will instantly gain $0.50 in value. 
* **The Catch:** As the stock moves, your Delta will actively change. It's only a snapshot.
* **Pro-Tip:** Traders also use Delta as a rough probability of the option expiring "In-The-Money". A 0.20 Delta option roughly has a 20% chance of being profitable at expiration.
''',
    "gamma": r'''
### 🎢 Gamma ($\Gamma$) — The Acceleration

Tells you exactly how fast your Delta is changing. It is the core measurement of an option's pure **explosiveness**.

* **Intuition:** If you're driving a car, Delta is your speed, and Gamma is your acceleration. If you slam on the gas pedal, you have high Gamma. 
* **The Danger Zone:** Gamma violently spikes the closer you get to Expiration Day if the stock price is lingering exactly at your strike price. This causes the option price to wildly swing back and forth with every tick of the stock.
''',
    "vega": r'''
### 🚨 Vega ($\mathcal{V}$) — The Panic Meter

Tells you how much the option price will mathematically spike or crash if implied volatility violently changes by **1%**.

* **Intuition:** Vega exists exclusively because of human emotion. Before a massive earnings report, traders panic and buy insurance, causing implied volatility to soar. If your Vega is high, just this *fear alone* will make your option incredibly expensive, even if the stock price hasn't moved a single inch!
* **The "Crush":** The moment the earnings report happens and the mystery is gone, fear drops to zero. If you bought high-Vega options, you will be instantly obliterated by "IV Crush".
''',
    "theta": r'''
### ⏳ Theta ($\Theta$) — The Bleeding Clock

Tells you exactly how much money your option is mathematically guaranteed to lose **every single day** just because time is passing.

* **Intuition:** Options are like ice cubes melting on a hot sidewalk. When you buy an option, you are fighting a ticking clock. Theta tells you how fast it's melting.
* **The Curve:** The bleeding doesn't happen evenly. If you have 2 years left, it melts very slowly. If you have 2 days left, it visibly evaporates before your eyes.
''',
    "rho": r'''
### 🏦 Rho ($\rho$) — The Bank Rate

Tells you how much the option value changes if the Federal Reserve randomly raises interest rates by **1%**.

* **Intuition:** It costs money to buy stock. Options give you a mathematical advantage because you control 100 shares for a fraction of the price, allowing you to leave the rest of your cash sitting safely in a high-yield bank account. The higher the bank's interest rate, the more valuable this "free cash" advantage gets.
* **The Reality:** For 99% of options traded (expiring in less than 3 months), Rho is virtually zero and completely ignored by traders. It only really matters for multi-year options (LEAPS).
'''
}

@dash.callback(
    Output("greek-description-output", "children"),
    Input("greeks-tabs", "active_tab")
)
def update_greek_description(active_tab: str):
    """Update the markdown formatted description based on the selected Greek tab."""
    if not active_tab:
        return dcc.Markdown("Select a Greek.", mathjax=True)
    greek_id = active_tab.replace("-tab", "")
    desc = GREEK_DESCRIPTIONS.get(greek_id, "Description not found.")
    return dcc.Markdown(desc, mathjax=True)

