"""
pricer_callbacks.py — Callbacks for the option pricer page.
"""

import dash
from dash import html, dcc, Input, Output, State
import plotly.graph_objects as go

from quantiv.pricing import Pricer
from quantiv.utils.formatting import format_price, format_greeks
from quantiv import _quantiv_engine

pricer = Pricer()
engine = _quantiv_engine.QuantivPortfolioEngine()


@dash.callback(
    Output("pricer-price-output", "children"),
    Output("pricer-greeks-output", "children"),
    Output("pricer-convergence-chart", "figure"),
    Input("btn-calculate-pricer", "n_clicks"),     # <--- ONLY THIS TRIGGERS THE CALLBACK NOW!
    State("pricer-spot", "value"),                 # <--- CHANGED TO STATE
    State("pricer-strike", "value"),               # <--- CHANGED TO STATE
    State("pricer-vol", "value"),                  # <--- CHANGED TO STATE
    State("pricer-rate", "value"),                 # <--- CHANGED TO STATE
    State("pricer-expiry", "value"),               # <--- CHANGED TO STATE
    State("pricer-model", "value"),                # <--- CHANGED TO STATE
    State("pricer-option-type", "value"),          # <--- CHANGED TO STATE
    State("session-user", "data")
)
def update_price(n_clicks, spot, strike, vol_pct, rate_pct, expiry, model, option_type, username):
    """Compute option price, manage credits, and update display ONLY on button click."""
    
    # 1. Prevent calculation when the page first loads
    if n_clicks is None:
        fig = go.Figure()
        fig.add_annotation(
            text="Click 'Calculate' to run models & generate charts.", 
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, 
            font=dict(size=16, color="#94a3b8")
        )
        fig.update_layout(template="plotly_dark", height=400, xaxis=dict(visible=False), yaxis=dict(visible=False))
        return "---", html.P("Awaiting execution...", className="text-muted"), fig

    try:
        vol = vol_pct / 100.0
        rate = rate_pct / 100.0

        # Calculate the basic Price & Greeks
        result = pricer.price(
            model=model, spot=spot, strike=strike,
            vol=vol, rate=rate, expiry=expiry,
            option_type=option_type,
        )

        price_text = format_price(result.price)

        greeks_div = html.Div([
            html.Table([
                html.Thead(html.Tr([html.Th("Greek"), html.Th("Value")])),
                html.Tbody([
                    html.Tr([html.Td(name.capitalize()), html.Td(f"{val:.6f}")])
                    for name, val in result.greeks.items()
                ]),
            ], className="table table-sm table-dark")
        ]) if result.greeks else html.P("No Greeks available for this model.")


        # 2. VISUALS & CREDITS PAYWALL LOGIC
        fig = go.Figure()
        
        # Check if they are logged in
        if not username:
            fig.add_annotation(
                text="🔒 Please log in via the Portfolio tab to view charts.", 
                xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, 
                font=dict(size=16, color="#ff4f6d")
            )
            fig.update_layout(template="plotly_dark", height=400, xaxis=dict(visible=False), yaxis=dict(visible=False))
            return price_text, greeks_div, fig
            
        # Check if they have credits (Deducts 1 credit automatically!)
        if not engine.use_advanced_feature(username):
            fig.add_annotation(
                text="⚡ Out of credits! Please upgrade your plan to view charts.", 
                xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, 
                font=dict(size=16, color="#f5c542")
            )
            fig.update_layout(template="plotly_dark", height=400, xaxis=dict(visible=False), yaxis=dict(visible=False))
            return price_text, greeks_div, fig


        # 3. Generate the actual chart if they passed the credit checks
        if model in ("binomial", "trinomial", "bopm"):
            steps_range = list(range(10, 201, 10))
            prices = []
            for s in steps_range:
                r = pricer.price(
                    model=model, spot=spot, strike=strike,
                    vol=vol, rate=rate, expiry=expiry,
                    option_type=option_type, steps=s,
                )
                prices.append(r.price)

            fig.add_trace(go.Scatter(
                x=steps_range, y=prices,
                mode="lines+markers",
                name=f"{model.upper()} Convergence",
                line=dict(color="#00d4ff"),
            ))

            bsm_result = pricer.price(
                model="bsm", spot=spot, strike=strike,
                vol=vol, rate=rate, expiry=expiry,
                option_type=option_type,
            )
            fig.add_hline(y=bsm_result.price, line_dash="dash",
                          line_color="yellow",
                          annotation_text="BSM Analytical")

        fig.update_layout(
            title="Model Convergence",
            xaxis_title="Number of Steps",
            yaxis_title="Option Price ($)",
            template="plotly_dark",
            height=400,
        )

        return price_text, greeks_div, fig

    except Exception as e:
        return str(e), html.P(f"Error: {e}"), go.Figure()


# ... (Keep MODEL_DESCRIPTIONS and the update_model_description callback here!) ...


# ── Dynamic Model Descriptions ──────────────────────────────────────────────

MODEL_DESCRIPTIONS = {
    "bsm": r'''
### 📈 Black-Scholes-Merton (BSM) Model
The **Black-Scholes-Merton** model is the granddaddy of all option pricing. It uses one massive, elegant math equation to instantly spit out the exact "fair price" of an option. 

**Intuition:**
* **The Smooth Wave:** It assumes the stock market acts like a completely smooth, continuous wave, and that the stock's volatility never ever changes.
* **The Perfect Hedge:** It figures out the option's value by pretending you could build a "risk-free" portfolio that perfectly balances the option and the stock at all times. 
* **The Catch:** It only works for "European" options, meaning you are strictly forced to wait until the exact Expiration Day to exercise your contract; you cannot exercise it over the weekend or a week early!

**Formulas:**
For a European Call ($C$) and Put ($P$):

$$
C = S_0 \Phi(d_1) - K e^{-rT} \Phi(d_2)
$$

$$
P = K e^{-rT} \Phi(-d_2) - S_0 \Phi(-d_1)
$$

where $\Phi(x)$ is the cumulative standard normal distribution and:

$$
d_1 = \frac{\ln(S_0/K) + (r + \sigma^2/2)T}{\sigma \sqrt{T}} \quad \text{and} \quad d_2 = d_1 - \sigma \sqrt{T}
$$

*Note: $d_1$ and $d_2$ represent mathematically how 'In-The-Money' your option is probabilistically relative to volatility and time.*

**Inputs & Outputs:**
* **Inputs:** Spot Price ($S_0$), Strike Price ($K$), Time to Expiry ($T$), Risk-Free rate ($r$), Volatility ($\sigma$).
* **Outputs:** Exact analytical Option Price and instantaneous Greeks (Delta, Gamma, Vega, Theta, Rho).
---
''',
    "binomial": r'''
### 🌳 Binomial Tree Model
Think of the **Binomial Tree** like a giant game of Plinko. Instead of one continuous math equation, this model breaks time down into hundreds of tiny, individual steps (like days or hours).

**Intuition:**
* **The Branching Path:** At every single step in the game, the stock price has only two choices: it can either bounce exactly one step "Up" or bounce exactly one step "Down".
* **Looking into the Future:** It maps out an enormous branching tree of every possible path the stock could take all the way to Expiration Day. 
* **Working Backwards:** It looks at how much money the option made at the very end of every branch, and works backwards step-by-step to figure out what the option is fairly worth *today*.
* **The American Advantage:** Because it checks the price at every single step, it is perfectly designed to price "American" options (options that you can exercise early at any time).

**Formulas:**
The Up factor ($u$), Down factor ($d$), and Risk-neutral probability ($p$):

$$
u = e^{\sigma \sqrt{\Delta t}} \quad \text{and} \quad d = \frac{1}{u}
$$

$$
p = \frac{e^{r \Delta t} - d}{u - d}
$$

Option Value at specific node $(i,j)$:

$$
V_{i,j} = \max\left( \text{Intrinsic Value}, e^{-r \Delta t} [p V_{i+1, j+1} + (1-p) V_{i+1, j-1}] \right)
$$

**Inputs & Outputs:**
* **Inputs:** Base parameters + **Steps** (tree depth). More numerical steps = better accuracy but takes longer to compute. 
* **Outputs:** American Options Price and finite-difference Greeks.
---
''',
    "trinomial": r'''
### 🌲 Trinomial Tree Model
The **Trinomial Tree** is exactly like the Binomial Tree's older, smarter brother. It simply adds a third option at every single step.

**Intuition:**
* **The Third Path:** Instead of fiercely forcing the stock to only bounce "Up" or "Down", this model allows the stock to calmly stay "Flat" (no movement) at any given step.
* **Smoothness:** Because stocks in real life often trade flat for hours, this model is much more realistic and smooth than the rigid Binomial tree. 
* **The Advantage:** It computes the true, accurate option price much faster than the Binomial tree, and prevents the complex math from loudly "jittering".

**Formulas:**
Option Value at specific node $(i,j)$ is a discounted expectation over precisely 3 distinct branches:

$$
V_{i,j} = e^{-r \Delta t} [p_u V_{i+1, j+1} + p_m V_{i+1, j} + p_d V_{i+1, j-1}]
$$

**Inputs & Outputs:**
* **Inputs:** Base mathematical parameters + **Steps** (controls geometric grid resolution).
* **Outputs:** Pre-early-exercise American Option Price and highly stable finite-difference Greeks. 
---
''',
    "monte_carlo": r'''
### 🎲 Monte Carlo Simulation
**Monte Carlo** is totally different from the others. Imagine rolling a massive handful of 10,000 dice to predict the future.

**Intuition:**
* **Random Chaos:** Instead of solving a strict math equation or building a rigid tree, this algorithm uses a massive random number generator to artificially simulate 10,000 completely different, wild, chaotic paths the stock *might* potentially take. 
* **The Law of Averages:** For every single one of those 10,000 hypothetical futures, it looks at how much money the option made. Then, it simply takes the mathematical average of all 10,000 results to give you the fair price!
* **Ultimate Flexibility:** It is the absolute gold standard for pricing weird, complex "exotic" options where the final payout depends on the *entire path* the stock took, not just where it ended up.

**Formulas:**
Simulating the terminal asset price ($S_T$) using Geometric Brownian Motion iterations:

$$
S_{t+\Delta t} = S_t \exp\left( (r - \frac{\sigma^2}{2})\Delta t + \sigma \sqrt{\Delta t} Z \right)
$$

Where $Z$ is a random draw from a standard normal distribution, $Z \sim N(0,1)$.

The estimated option price is the discounted expected payoff across all $M$ randomized paths:

$$
C = e^{-rT} \frac{1}{M} \sum_{i=1}^{M} \max(S_T^{(i)} - K, 0)
$$

**Inputs & Outputs:**
* **Inputs:** Base parameters + **Paths** (number of isolated random walk simulations, $M$).
* **Outputs:** Stochastically Simulated Option Price. *Warning: Estimating precise Greeks requires immense compute topology (running millions of grouped paths).*
---
'''
}

@dash.callback(
    Output("model-description-output", "children"),
    Input("pricer-model", "value")
)
def update_model_description(model: str):
    """Update the markdown formatted description based on the selected model."""
    desc = MODEL_DESCRIPTIONS.get(model, "Description not found.")
    return dcc.Markdown(desc, mathjax=True)
