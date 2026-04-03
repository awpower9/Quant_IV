"""
pricer_callbacks.py — Callbacks for the option pricer page.
Includes standard BSM/Tree/MC models and Pro-tier Heston & Merton models.
"""

import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from quantiv.pricing import Pricer
# from quantiv.pricing.quantiv_pro_engine import price_heston, price_merton  # DELETED
from quantiv.utils.formatting import format_price, format_greeks
from quantiv import _quantiv_engine
from dashboard.components.advanced_visuals import get_heston_vol_surface, get_merton_pdf_comparison

pricer = Pricer()
engine = _quantiv_engine.QuantivPortfolioEngine()
pro_engine = _quantiv_engine.ProEngine()


# ══════════════════════════════════════════════════════════════════════════════
# 1. DYNAMIC ADVANCED SLIDER INJECTION
# ══════════════════════════════════════════════════════════════════════════════

def _get_locked_overlay():
    """A sleek, blurred overlay blocking access and routing users to upgrade."""
    return html.Div(
        className="text-center p-4 mt-3",
        style={
            "backdropFilter": "blur(8px)",
            "backgroundColor": "rgba(20, 20, 20, 0.7)",
            "borderRadius": "12px",
            "border": "1px solid #333",
            "boxShadow": "0 8px 32px 0 rgba(0, 0, 0, 0.37)"
        },
        children=[
            html.H1("🔒", className="display-4 text-warning mb-2"),
            html.H5("PRO FEATURE", className="text-warning fw-bold"),
            html.P("Upgrade your plan to unlock Advanced Stochastic & Jump-Diffusion Models.",
                   className="text-light mb-3", style={"fontSize": "0.9rem"}),
            dbc.Button(
                "UPGRADE NOW →",
                href="/subscription",
                color="warning",
                className="fw-bold px-4 py-2 rounded-pill shadow-lg"
            )
        ]
    )


@dash.callback(
    Output("advanced-sliders-container", "children"),
    Output("pro-params-store", "data"),
    Input("pricer-model", "value"),
    State("session-user", "data"),
)
def render_advanced_sliders(selected_model, username):
    """Injects the extra parameter sliders and writes defaults to pro-params-store."""

    # Paywall Check: Must be logged in AND on Pro tier
    if selected_model in ("heston", "merton"):
        if not username:
            return _get_locked_overlay(), {}
        tier = engine.get_subscription_tier(username)
        if tier != "Pro":
            return _get_locked_overlay(), {}

    # Render Heston Sliders
    if selected_model == "heston":
        defaults = {"kappa": 2.0, "theta": 0.04, "sigma_v": 0.3, "rho": -0.7}
        sliders = html.Div([
            html.Hr(className="my-3"),
            html.H6("⚙️ Heston Parameters", className="text-info fw-bold mb-3"),

            html.Label("κ (Mean Reversion Speed)", className="mt-1 small"),
            dcc.Slider(id="slider-kappa", min=0.1, max=5, step=0.1, value=2.0,
                       marks=None, tooltip={"placement": "bottom"}),

            html.Label("θ (Long-Term Variance)", className="mt-2 small"),
            dcc.Slider(id="slider-theta", min=0.01, max=0.5, step=0.01, value=0.04,
                       marks=None, tooltip={"placement": "bottom"}),

            html.Label("σᵥ (Vol of Volatility)", className="mt-2 small"),
            dcc.Slider(id="slider-sigma-v", min=0.01, max=1.0, step=0.01, value=0.3,
                       marks=None, tooltip={"placement": "bottom"}),

            html.Label("ρ (Price/Vol Correlation)", className="mt-2 small"),
            dcc.Slider(id="slider-rho", min=-1.0, max=1.0, step=0.05, value=-0.7,
                       marks=None, tooltip={"placement": "bottom"}),
        ])
        return sliders, defaults

    # Render Merton Sliders
    elif selected_model == "merton":
        defaults = {"lamb": 1.0, "muj": -0.15, "sigmaj": 0.20}
        sliders = html.Div([
            html.Hr(className="my-3"),
            html.H6("⚙️ Merton Jump Parameters", className="text-info fw-bold mb-3"),

            html.Label("λ (Expected Jumps/Year)", className="mt-1 small"),
            dcc.Slider(id="slider-lambda", min=0, max=5, step=0.1, value=1.0,
                       marks=None, tooltip={"placement": "bottom"}),

            html.Label("μⱼ (Mean Jump Size)", className="mt-2 small"),
            dcc.Slider(id="slider-muj", min=-0.5, max=0.5, step=0.01, value=-0.15,
                       marks=None, tooltip={"placement": "bottom"}),

            html.Label("σⱼ (Jump Volatility)", className="mt-2 small"),
            dcc.Slider(id="slider-sigmaj", min=0.01, max=0.5, step=0.01, value=0.20,
                       marks=None, tooltip={"placement": "bottom"}),
        ])
        return sliders, defaults

    # Standard model — clear the container
    return html.Div(), {}


# ══════════════════════════════════════════════════════════════════════════════
# 2. MASTER PRICING CALLBACK
# ══════════════════════════════════════════════════════════════════════════════

@dash.callback(
    Output("pricer-price-output", "children"),
    Output("pricer-greeks-output", "children"),
    Output("pricer-convergence-chart", "figure"),
    Input("btn-calculate-pricer", "n_clicks"),     # <--- ONLY THIS TRIGGERS
    State("pricer-spot", "value"),
    State("pricer-strike", "value"),
    State("pricer-vol", "value"),
    State("pricer-rate", "value"),
    State("pricer-expiry", "value"),
    State("pricer-model", "value"),
    State("pricer-option-type", "value"),
    State("session-user", "data"),
    State("pro-params-store", "data"),              # <--- All pro params in one store
)
def update_price(n_clicks, spot, strike, vol_pct, rate_pct, expiry, model,
                 option_type, username, pro_params):
    """Compute option price, manage credits, and update display ONLY on button click."""
    pro_params = pro_params or {}
    kappa = pro_params.get('kappa', 2.0)
    theta = pro_params.get('theta', 0.04)
    sigma_v = pro_params.get('sigma_v', 0.3)
    rho = pro_params.get('rho', -0.7)
    lamb = pro_params.get('lamb', 1.0)
    muj = pro_params.get('muj', -0.15)
    sigmaj = pro_params.get('sigmaj', 0.20)
    
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

        # ─────────────────────────────────────────────────────────────────
        # HESTON MODEL (PRO)
        # ─────────────────────────────────────────────────────────────────
        if model == "heston":
            # Paywall: Must be logged in AND Pro tier
            if not username:
                return _locked_price_output()
            tier = engine.get_subscription_tier(username)
            if tier != "Pro":
                return _locked_price_output()

            # Check credits (deducts 1)
            if not engine.use_advanced_feature(username):
                return _no_credits_output()

            # Safe defaults if sliders haven't rendered
            kappa = kappa or 2.0
            theta = theta or 0.04
            sigma_v = sigma_v or 0.3
            rho = rho or -0.7
            v0 = vol ** 2  # Starting variance from base vol slider

            o_type = _quantiv_engine.OptionType.Call if option_type.lower() == "call" else _quantiv_engine.OptionType.Put
            option = _quantiv_engine.Option(strike, expiry, o_type)
            market = _quantiv_engine.MarketData(spot, vol, rate)

            result = pro_engine.price_heston(option, market, kappa, theta, sigma_v, rho)
            price_text = format_price(result.price)

            greeks_div = html.Div([
                html.Table([
                    html.Thead(html.Tr([html.Th("Greek"), html.Th("Value")])),
                    html.Tbody([
                        html.Tr([html.Td("Delta (Δ)"), html.Td(f"{result.greeks.get('delta', 0.0):.6f}")]),
                        html.Tr([html.Td("Gamma (Γ)"), html.Td(f"{result.greeks.get('gamma', 0.0):.6f}")]),
                    ]),
                ], className="table table-sm table-dark")
            ])

            fig = get_heston_vol_surface()
            return price_text, greeks_div, fig

        # ─────────────────────────────────────────────────────────────────
        # MERTON MODEL (PRO)
        # ─────────────────────────────────────────────────────────────────
        elif model == "merton":
            # Paywall: Must be logged in AND Pro tier
            if not username:
                return _locked_price_output()
            tier = engine.get_subscription_tier(username)
            if tier != "Pro":
                return _locked_price_output()

            # Check credits (deducts 1)
            if not engine.use_advanced_feature(username):
                return _no_credits_output()

            # Safe defaults
            lamb = lamb or 1.0
            muj = muj or -0.15
            sigmaj = sigmaj or 0.20

            o_type = _quantiv_engine.OptionType.Call if option_type.lower() == "call" else _quantiv_engine.OptionType.Put
            option = _quantiv_engine.Option(strike, expiry, o_type)
            market = _quantiv_engine.MarketData(spot, vol, rate)

            result = pro_engine.price_merton(option, market, lamb, muj, sigmaj)
            price_text = format_price(result.price)

            greeks_div = html.Div([
                html.Table([
                    html.Thead(html.Tr([html.Th("Greek"), html.Th("Value")])),
                    html.Tbody([
                        html.Tr([html.Td("Delta (Δ)"), html.Td(f"{result.greeks.get('delta', 0.0):.6f}")]),
                        html.Tr([html.Td("Gamma (Γ)"), html.Td(f"{result.greeks.get('gamma', 0.0):.6f}")]),
                    ]),
                ], className="table table-sm table-dark")
            ])

            fig = get_merton_pdf_comparison()
            return price_text, greeks_div, fig

        # ─────────────────────────────────────────────────────────────────
        # STANDARD MODELS (BSM, Binomial, Trinomial, Monte Carlo)
        # ─────────────────────────────────────────────────────────────────
        else:
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


            # VISUALS & CREDITS PAYWALL LOGIC
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


            # Generate the actual chart if they passed the credit checks
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
            else:
                model_name_map = {"bsm": "BSM Analytical", "monte_carlo": "Monte Carlo"}
                display_name = model_name_map.get(model, model.upper())
                fig.add_annotation(
                    text=f"The {display_name} model does not use tree step convergence.",
                    xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, 
                    font=dict(size=14, color="#94a3b8")
                )
                fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False))

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


# ══════════════════════════════════════════════════════════════════════════════
# 3. HELPER FUNCTIONS FOR LOCKED / NO-CREDIT STATES
# ══════════════════════════════════════════════════════════════════════════════

def _locked_price_output():
    """Return tuple for locked (not logged in) state."""
    fig = go.Figure()
    fig.add_annotation(
        text="🔒 Please log in via the Portfolio tab to access Pro models.",
        xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color="#ff4f6d")
    )
    fig.update_layout(template="plotly_dark", height=400, xaxis=dict(visible=False), yaxis=dict(visible=False))
    return "N/A", html.Div([
        html.H5("🔒 PRO FEATURE", className="text-warning fw-bold"),
        html.P("Log in to run Advanced Analytics.")
    ], className="text-center p-3"), fig


def _no_credits_output():
    """Return tuple for out-of-credits state."""
    fig = go.Figure()
    fig.add_annotation(
        text="⚡ Out of credits! Upgrade your plan for Pro models.",
        xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color="#f5c542")
    )
    fig.update_layout(template="plotly_dark", height=400, xaxis=dict(visible=False), yaxis=dict(visible=False))
    return "N/A", html.Div([
        html.H5("⚡ No Credits", className="text-warning fw-bold"),
        html.P("Upgrade your plan to access Advanced Models.")
    ], className="text-center p-3"), fig


# ══════════════════════════════════════════════════════════════════════════════
# 4. DYNAMIC MODEL DESCRIPTIONS (INCLUDING PRO MODELS)
# ══════════════════════════════════════════════════════════════════════════════

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
''',
    "heston": r'''
### 🌪️ The Heston Stochastic Volatility Model

**The Intuition:**
The traditional Black-Scholes model assumes that a stock's volatility is a constant, flat number. However, in the real world, volatility is dynamic and unpredictable—it rises during market crashes and drops during bull runs. The Heston Model fixes this by treating **volatility itself as a random, moving variable**. 

By allowing volatility and asset price to be correlated (when prices drop, volatility suddenly spikes), the Heston Model naturally recreates the famous **"Volatility Smile"** seen in real-world options trading matrices. It is superior to Black-Scholes because it accurately prices deep Out-Of-The-Money (OTM) options, which are historically heavily mispriced by constant-volatility models.

---

**The Math (SDEs):**
The Heston model defines the dynamics of the asset price ($S_t$) and its variance ($v_t$) using the following coupled Stochastic Differential Equations (SDEs):

$$
dS_t = \mu S_t dt + \sqrt{v_t} S_t dW_1^t
$$

$$
dv_t = \kappa (\theta - v_t) dt + \sigma_v \sqrt{v_t} dW_2^t
$$

Where the two Wiener processes (Brownian motions) are correlated:

$$
dW_1^t dW_2^t = \rho dt
$$

---

**Model Parameters:**

| Parameter | Symbol | Description |
|-----------|:---:|-------------|
| **Mean Reversion Rate** | $\kappa$ | How fast the variance violently snaps back to its long-term average. |
| **Long-Term Variance** | $\theta$ | The normal, resting historical average variance of the asset. |
| **Vol of Volatility** | $\sigma_v$ | Determines how sharply the variance jumps around itself (kurtosis). |
| **Correlation** | $\rho$ | The correlation between the asset's price and variance. Usually negative for equities (prices drop -> panic spikes). |
---
''',
    "merton": r'''
### 🦢 The Merton Jump-Diffusion Model

**The Intuition:**
The Black-Scholes model assumes that asset prices move in continuous, smooth, extremely tiny steps (Brownian motion). Because of this, it assumes that massive daily drops (like the 1987 Black Monday crash or abrupt earnings gaps) are statistically impossible. The Merton Jump-Diffusion model fixes this fatal flaw by adding **"Black Swan" jump events** directly into the math.

It combines a standard smooth diffusion process with a Poisson "jump" process. When a jump triggers, the stock price teleports instantly without trading at any prices in between. This makes it an incredibly powerful model for pricing options surrounding severe unannounced news, catastrophic events, and massive overnight gaps.

---

**The Math (SDEs):**
The asset price ($S_t$) is driven by both a continuous diffusion process and a discrete Poisson jump process ($N_t$):

$$
\frac{dS_t}{S_{t-}} = (\mu - \lambda k) dt + \sigma dW_t + (J_t - 1) dN_t
$$

Where:
* $dW_t$ is a standard Wiener process (smooth volatility noise).
* $dN_t$ is a Poisson process generating random times of jumps with intensity $\lambda$.
* $J_t$ is the random jump size (log-normally distributed).
* $k = \mathbb{E}[J_t - 1]$ is the expected percentage jump size, serving to keep the drift mathematically fair.

---

**Model Parameters:**

| Parameter | Symbol | Description |
|-----------|:---:|-------------|
| **Jump Intensity** | $\lambda$ | The expected number of massive jump events per year. |
| **Mean Jump Size** | $\mu_j$ | The average expected magnitude of the jump (negative means downward crashes are more likely). |
| **Jump Volatility** | $\sigma_j$ | The standard deviation / sheer unpredictability of the jump size. |
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
