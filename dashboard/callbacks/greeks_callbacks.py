"""
greeks_callbacks.py — Callbacks for the Greeks dashboard page.
"""

import dash
from dash import Input, Output, dcc
import plotly.graph_objects as go

from quantiv.analytics import GreeksAnalyzer

analyzer = GreeksAnalyzer()


@dash.callback(
    Output("greeks-chart", "figure"),
    Input("greeks-spot", "value"),
    Input("greeks-strike", "value"),
    Input("greeks-vol", "value"),
    Input("greeks-rate", "value"),
    Input("greeks-expiry", "value"),
    Input("greeks-option-type", "value"),
    Input("greeks-tabs", "active_tab"),
)
def update_greeks_chart(spot, strike, vol_pct, rate_pct, expiry,
                        option_type, active_tab):
    """Update the Greeks chart based on the selected tab."""
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

        fig = go.Figure()
        if greek_name in df.columns:
            fig.add_trace(go.Scatter(
                x=df["spot"], y=df[greek_name],
                mode="lines",
                name=greek_name.capitalize(),
                line=dict(color="#00d4ff", width=2),
                fill="tozeroy",
                fillcolor="rgba(0, 212, 255, 0.1)",
            ))

            # Mark current spot
            fig.add_vline(x=spot, line_dash="dash", line_color="yellow",
                          annotation_text="Current Spot")

        fig.update_layout(
            title=f"{greek_name.capitalize()} vs Spot Price",
            xaxis_title="Spot Price ($)",
            yaxis_title=greek_name.capitalize(),
            template="plotly_dark",
            height=500,
        )

        return fig

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Error: {e}", showarrow=False)
        fig.update_layout(template="plotly_dark")
        return fig


# ── Dynamic Greeks Dictionary ─────────────────────────────────────────────
GREEK_DESCRIPTIONS = {
    "delta": r"""
### ⨤ Delta ($\Delta$) : The Speedometer
**Delta** is the option's "speed". It tells you exactly how much your option's price will dynamically change if the underlying stock moves by exactly $\$1.00$.

**Mathematical Definition:**

$$
\Delta = \frac{\partial V}{\partial S}
$$

For a European Call and Put under BSM:

$$
\Delta_{call} = \Phi(d_1) \quad \text{and} \quad \Delta_{put} = \Phi(d_1) - 1
$$

**Intuition:**
* **The $\$1$ Rule:** If Delta is 0.60, and the stock price suddenly jumps up by $\$1$, your option will instantly become $\sim\$0.60$ more valuable. 
* **The Odds Cheat-Code:** Traders constantly use Delta as a quick hack to guess the odds of winning. A Delta of 0.60 intuitively means the market broadly estimates there is a ~60% chance this option will successfully finish "In-The-Money".
""",
    "gamma": r"""
### ℽ Gamma ($\Gamma$) : The Accelerator
**Gamma** is the option's "acceleration". While Delta tells you your current cruising speed, Gamma tells you how aggressively your Speed is going to change if you step heavily on the gas pedal.

**Mathematical Definition:**

$$
\Gamma = \frac{\partial^2 V}{\partial S^2} = \frac{\partial \Delta}{\partial S}
$$

**Intuition:**
* **The Speed Boost:** As the stock price moves higher, Gamma physically adds fuel to your Delta, making your option price move even faster!
* **Dangerous Swings:** Gamma peaks powerfully when you are exactly "At-The-Money" and right about to expire. The option's price can violently whip back and forth, making it extremely dangerous for short sellers.
""",
    "vega": r"""
### $\nu$ Vega ($\mathcal{V}$) : The Weather Forecast
**Vega** acts like the market's "weather forecast". It measures exactly how sensitive your option is to sudden panic, fear, or excitement in the overall market (Implied Volatility).

**Mathematical Definition:**

$$
\mathcal{V} = \frac{\partial V}{\partial \sigma}
$$

**Intuition:**
* **Fear is Expensive:** If Vega is 0.15, and a sudden news scandal makes the stock market 1% more volatile (fear goes up), your option's price will instantly rise by roughly $\$0.15$ just because people are scrambling to buy insurance.
* **Turtles vs Rabbits:** Vega is highest when you have months and months left until Expiration, because there is an immense amount of time for crazy market crashes to randomly happen.
""",
    "theta": r"""
### $\Theta$ Theta ($\Theta$) : The Ticking Clock
**Theta** is a brutal "fuel leak" built permanently into your option. Because options have an expiration date, they physically lose value every single day that safely passes without any drama.

**Mathematical Definition:**

$$
\Theta = \frac{\partial V}{\partial t} = -\frac{\partial V}{\partial T}
$$

**Intuition:**
* **The Daily Tax:** If your option's Theta is strictly `-0.05`, you will passively bleed $\$0.05$ of fundamental value every single market day, doing absolutely nothing!
* **The Final Countdown:** This leak isn't perfectly steady. As you get horrifyingly close to Expiration Friday, Theta accelerates into a massive free-fall as the remaining time value physically evaporates into thin air.
""",
    "rho": r"""
### $\rho$ Rho ($\rho$) : The Toll Booth
**Rho** is the tiny background effect that the central macro risk-free interest rate (like Federal Treasury yields) has on your option's exact price.

**Mathematical Definition:**

$$
\rho = \frac{\partial V}{\partial r}
$$

**Intuition:**
* **Call Options love High Rates:** If Rho is $0.05$, a 1% localized hike in the primary federal interest rate will ironically cause your Call option's price to permanently rise by precisely $\$0.05$. 
* Why? Because high interest rates mathematically heavily reduce the "future" cost of buying the physical stock later. Consequently, Put options actively lose value during high rates.
"""
}

@dash.callback(
    Output("greeks-description-output", "children"),
    Input("greeks-tabs", "active_tab")
)
def update_greek_description(active_tab: str):
    """Outputs dynamically parsed mathematical LaTeX markup per active tab focus."""
    base_name = active_tab.replace("-tab", "")
    desc = GREEK_DESCRIPTIONS.get(base_name, "Description not found.")
    return dcc.Markdown(desc, mathjax=True)
