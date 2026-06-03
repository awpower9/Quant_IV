"""
strategy_callbacks.py — Callbacks for the option strategy builder page.

These callbacks link the Dash UI to the quantiv.analytics layer.
They integrate with the C++ engine to manage user credits for visuals.
"""

import dash
from dash import html, dcc, Input, Output, State
import plotly.graph_objects as go

from quantiv.analytics.strategy_builder import StrategyBuilder
from quantiv.portfolio_engine import QuantivPortfolioEngine
from quantiv.utils.formatting import format_price
from quantiv.pricing import Pricer

builder = StrategyBuilder()
engine = QuantivPortfolioEngine()
pricer = Pricer()


# ── Dynamic Strategy Descriptions ─────────────────────────────────────────────
STRATEGY_DESCRIPTIONS = {
    "straddle": r"""
### ⚖️ Long Straddle
A **Long Straddle** is a major volatility strategy constructed by simultaneously buying a Call option and a Put option with the exact same Strike Price ($K$) and Expiry Date ($T$).

**Intuition:**
* **The Earthquake Warning:** You strongly suspect an enormous earthquake (like a massive earnings report) is about to happen, but you have literally no idea if the stock will jump straight up or completely crash down. You buy both a Call and a Put!
* **The Payout:** If the stock violently explodes upwards, the Call option prints money. If the stock violently crashes, the Put option prints money. 
* **The Catch:** Because you bought *two* options, it highly double-charges you upfront. The only way you lose is if the stock stays incredibly boring and perfectly flat.

**Mathematical Profile:**
* **Max Profit:** Unlimited (if Spot $\to \infty$) or substantially high (if Spot $\to 0$).
* **Max Risk (Loss):** Limited completely to the combined upfront premium paid: $C_{premium} + P_{premium}$.
* **Upper Breakeven:** $K + C_{premium} + P_{premium}$
* **Lower Breakeven:** $K - (C_{premium} + P_{premium})$
""",
    "bull_call": r"""
### 📈 Bull Call Spread
A **Bull Call Spread** is an intelligent directional strategy. You buy a Call option near the current price ($K_1$), but safely sell another Call option further Out-Of-The-Money ($K_2$) to collect some quick cash back.

**Intuition:**
* **The Discount:** Naked Call options are incredibly expensive. By instantly selling the higher-up Call option to someone else, you heavily subsidize and discount the upfront cost of your entire trade! 
* **The Ceiling:** Because you sold that second higher Call option, you gave up your right to any profits physically above that specific roof price. 
* **The Trade-Off:** You are sacrificing the dream of "unlimited lottery gains" in exchange for making the trade massively cheaper and vastly more likely to naturally succeed.

**Mathematical Profile:**
* **Max Profit:** Difference between Strikes minus the net premium paid: $(K_2 - K_1) - \text{Net Premium}$.
* **Max Risk (Loss):** Strictly limited to the net premium paid upfront.
* **Breakeven:** $K_1 + \text{Net Premium}$
""",
    "bear_put": r"""
### 📉 Bear Put Spread
A **Bear Put Spread** is a smart bearish strategy. You buy a Put option to aggressively bet on a crash ($K_2$), but simultaneously sell an even lower Put option ($K_1$) to claw some cash back.

**Intuition:**
* **The Cheaper Short:** You are moderately bearish on the stock, but buying a raw Put option is too pricey. You buy a Put to heavily profit from a downward sink, but instantly sell the lower Put to significantly reduce your upfront cash cost.
* **The Floor:** This permanently caps your maximal profit if the stock tragically drops completely to $0 (since your sold Put acts as a floor), but massively increases your fundamental Return on Capital for highly probable, normal-sized moderate drops.

**Mathematical Profile:**
* **Max Profit:** Difference between Strikes minus the net premium paid: $(K_2 - K_1) - \text{Net Premium}$.
* **Max Risk (Loss):** Strictly limited to the net premium paid upfront.
* **Breakeven:** $K_2 - \text{Net Premium}$
""",
    "iron_condor": r"""
### 🦅 Iron Condor
An **Iron Condor** is a pure "Income Strategy". You sell options heavily on both sides to collect premium money upfront, and use a tiny portion of that income to purchase "disaster insurance" options far away to stay mathematically safe.

**Intuition:**
* **Betting on Boredom:** You are heavily betting that the stock is painfully boring, entirely range-bound, and will **NOT** dramatically move anywhere before expiration. 
* **The Cage:** You essentially build a "cage" around the current stock price. If the stock calmly stays inside the cage until Expiration Friday, all the sold options expire completely worthless, and you absolutely keep 100% of the upfront premium!
* **Safe Caps:** Your purchased outer "wings" guarantee that if an unexpected disaster strikes, your max catastrophic loss is rigidly capped.

**Mathematical Profile:**
* **Max Profit:** Strictly limited to the absolute net premium collected upfront.
* **Max Risk (Loss):** Width of the widest spread minus the net premium collected: $(K_2 - K_1) - \text{Net Premium}$.
* **Upper Breakeven:** $K_3 + \text{Net Premium}$
* **Lower Breakeven:** $K_2 - \text{Net Premium}$
""",
    "custom": r"""
### 🛠️ Custom Strategy
A **Custom Strategy** is your ultimate sandbox. It allows you to arbitrarily mix and match multiple option legs (trading Calls, Puts, long buys, short sells) across various distinct strike prices to build highly complex, deeply personalized structural payoffs!

**Intuition:**
* **Advanced Mechanics:** Real-world hedge fund traders dynamically adjust entirely custom legs on the fly to "roll" strikes up and down for credits. 
* **The Sandbox:** This highly advanced tool visually renders exactly what bizarre "Frankenstein" strategies (like uneven Iron Butterflies or massively asymmetric Ratio Spreads) look like structurally.
"""
}


@dash.callback(
    Output("strategy-payoff-chart", "figure"),
    Output("strategy-summary", "children"),
    Output("strategy-description-output", "children"),
    Input("btn-calculate-strategy", "n_clicks"),     # <--- ONLY THIS TRIGGERS THE CALLBACK
    State("strategy-selector", "value"),
    State("strategy-spot", "value"),
    State("strategy-strike1", "value"),
    State("strategy-strike2", "value"),
    State("strategy-expiry", "value"),
    State("session-user", "data"),                   # <--- GETS THE LOGGED-IN USER
)
def update_strategy(n_clicks, strategy_type, spot, strike1, strike2, expiry, username):
    """Update strategy payoff diagram with paywall and credit checks."""
    
    fig = go.Figure()
    desc_md = dcc.Markdown(STRATEGY_DESCRIPTIONS.get(strategy_type, ""), mathjax=True)
    
    # 1. Prevent calculation when the page first loads
    if n_clicks is None:
        fig.add_annotation(
            text="Click 'Generate Payoff' to build strategy & view chart.", 
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, 
            font=dict(size=16, color="#94a3b8")
        )
        fig.update_layout(template="plotly_dark", height=500, xaxis=dict(visible=False), yaxis=dict(visible=False))
        return fig, html.Div(), desc_md

    # 2. Login Check
    if not username:
        fig.add_annotation(
            text="🔒 Please log in via the Portfolio tab to view charts.", 
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, 
            font=dict(size=16, color="#ff4f6d")
        )
        fig.update_layout(template="plotly_dark", height=500, xaxis=dict(visible=False), yaxis=dict(visible=False))
        return fig, html.Div(), desc_md
        
    # 3. Credit Check (Deducts 1 credit automatically if true!)
    if not engine.use_advanced_feature(username):
        fig.add_annotation(
            text="⚡ Out of credits! Please upgrade your plan to view charts.", 
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, 
            font=dict(size=16, color="#f5c542")
        )
        fig.update_layout(template="plotly_dark", height=500, xaxis=dict(visible=False), yaxis=dict(visible=False))
        return fig, html.Div(), desc_md

    # 4. Generate the actual chart if they passed the credit checks
    try:
        # Get premiums from BSM pricer to construct the legs
        call1 = pricer.price(model="bsm", spot=spot, strike=strike1, vol=0.2, rate=0.05, expiry=expiry, option_type="call")
        put1 = pricer.price(model="bsm", spot=spot, strike=strike1, vol=0.2, rate=0.05, expiry=expiry, option_type="put")
        call2 = pricer.price(model="bsm", spot=spot, strike=strike2, vol=0.2, rate=0.05, expiry=expiry, option_type="call")

        # Build the requested strategy
        if strategy_type == "straddle":
            strategy = StrategyBuilder.long_straddle(strike1, expiry, call1.price, put1.price)
        elif strategy_type == "bull_call":
            strategy = StrategyBuilder.bull_call_spread(strike1, strike2, expiry, call1.price, call2.price)
        elif strategy_type == "bear_put":
            put2 = pricer.price(model="bsm", spot=spot, strike=strike2, vol=0.2, rate=0.05, expiry=expiry, option_type="put")
            strategy = StrategyBuilder.bear_put_spread(strike1, strike2, expiry, put1.price, put2.price)
        else:
            # Default fallback
            strategy = StrategyBuilder.long_straddle(strike1, expiry, call1.price, put1.price)

        # Compute the payoff curve array
        df = StrategyBuilder.compute_payoff(strategy, (spot * 0.5, spot * 1.5))

        # Add the main curve
        fig.add_trace(go.Scatter(
            x=df["spot"], y=df["profit"], 
            mode="lines", name="P&L at Expiry", 
            line=dict(color="#00d4ff", width=2)
        ))
        
        # Add visual markers (Zero-line and Current Spot)
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.add_vline(x=spot, line_dash="dash", line_color="yellow", annotation_text="Current Spot")

        # Format the chart
        fig.update_layout(
            title=f"{strategy.name} — P&L at Expiry", 
            xaxis_title="Spot Price at Expiry ($)", 
            yaxis_title="Profit/Loss ($)", 
            template="plotly_dark", 
            height=500
        )

        # Build the HTML summary of the exact legs used
        summary = html.Div([
            html.H5(strategy.name),
            html.Ul([
                html.Li(f"{'Long' if l.position == 'long' else 'Short'} {l.option_type.capitalize()} @ K={l.strike:.0f}, Premium=${l.premium:.2f}") 
                for l in strategy.legs
            ]),
        ])

        return fig, summary, desc_md

    except Exception as e:
        # Failsafe error rendering
        fig = go.Figure()
        fig.add_annotation(text=f"Error computing strategy: {e}", showarrow=False, font=dict(color="#ff4f6d"))
        fig.update_layout(template="plotly_dark", height=500, xaxis=dict(visible=False), yaxis=dict(visible=False))
        return fig, html.P(f"Error: {e}", className="text-danger"), desc_md
