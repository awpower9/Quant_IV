import numpy as np
import plotly.graph_objects as go
import math

def get_heston_vol_surface(params=None):
    """
    Generates a 3D surface plot demonstrating the Heston Implied Volatility Surface.
    Highlights how the 'smile' is heavily skewed at short maturities and flattens out over time.
    """
    # 1. Create the Strike (X) and Maturity (Y) grids
    strikes = np.linspace(70, 130, 40)
    maturities = np.linspace(0.1, 2.0, 40)
    K, T = np.meshgrid(strikes, maturities)
    
    # 2. Render a dynamic Stylized Heston Smile (optimized for Plotly 3D UI performance)
    # In real models, IV = base + skew*(Moneyness/sqrt(T)) + convexity*(Moneyness^2 / T)
    S = 100.0
    moneyness = np.log(K / S)
    
    # Synthetic Heston profile: negative skew (equity panic) + heavy short-term kurtosis
    IV = 0.20 - 0.15 * (moneyness / np.sqrt(T)) + 0.10 * (moneyness**2 / T)
    IV = np.clip(IV, 0.05, 0.80) # Cap bounds for visual sanity
    
    # 3. Build the 3D Surface Figure
    fig = go.Figure(data=[go.Surface(
        x=K, 
        y=T, 
        z=IV, 
        colorscale='PuBu',   # Purple to Blue theme matching QuantIV styling
        contours=dict(
            z=dict(show=True, usecolormap=True, highlightcolor="white", project_z=True)
        )
    )])
    
    fig.update_layout(
        title=dict(text="Heston Implied Volatility Surface", font=dict(color="#E0E0E0", size=18)),
        scene=dict(
            xaxis_title="Strike Price",
            yaxis_title="Time to Maturity (Yrs)",
            zaxis_title="Implied Volatility",
            xaxis=dict(gridcolor="rgba(255,255,255,0.1)", backgroundcolor="rgba(0,0,0,0)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.1)", backgroundcolor="rgba(0,0,0,0)"),
            zaxis=dict(gridcolor="rgba(255,255,255,0.1)", backgroundcolor="rgba(0,0,0,0)"),
            camera=dict(eye=dict(x=1.5, y=-1.5, z=0.5)) # Optimal default viewing angle
        ),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, b=0, t=40)
    )
    return fig


def get_merton_pdf_comparison(params=None):
    """
    Generates a line chart comparing the Black-Scholes Lognormal PDF against the 
    Merton Jump-Diffusion PDF to visually highlight 'Fat Tails' and crash risks.
    """
    # 1. Standardize Parameters
    S0 = 100; r = 0.05; T = 1.0; sigma = 0.15 
    lamb = 1.0        # Expected 1 jump per year
    mu_j = -0.15      # Jumps are usually 15% downward crashes on average
    sigma_j = 0.20    # High uncertainty in crash magnitude
    
    x = np.linspace(40, 170, 500)
    
    # 2. Compute Black-Scholes PDF (Standard Smooth Lognormal)
    bs_mean = np.log(S0) + (r - 0.5 * sigma**2) * T
    bs_std = sigma * np.sqrt(T)
    pdf_bs = (1 / (x * bs_std * np.sqrt(2 * np.pi))) * np.exp(-((np.log(x) - bs_mean)**2) / (2 * bs_std**2))
    
    # 3. Compute Merton PDF (Poisson-weighted sum of conditional lognormals)
    pdf_merton = np.zeros_like(x)
    k_j = np.exp(mu_j + 0.5 * sigma_j**2) - 1  # Drift compensator
    
    for n in range(12): # Sum 12 possible jump occurrences
        prob_n = np.exp(-lamb * T) * ((lamb * T)**n) / math.factorial(n)
        
        var_n = sigma**2 * T + n * sigma_j**2
        std_n = np.sqrt(var_n)
        mean_n = np.log(S0) + (r - lamb * k_j) * T + n * mu_j - 0.5 * var_n
        
        pdf_n = (1 / (x * std_n * np.sqrt(2 * np.pi))) * np.exp(-((np.log(x) - mean_n)**2) / (2 * std_n**2))
        pdf_merton += prob_n * pdf_n

    # 4. Build the Interactive Plotly Chart
    fig = go.Figure()

    # Black-Scholes Curve
    fig.add_trace(go.Scatter(
        x=x, y=pdf_bs, mode="lines",
        name="Black-Scholes (No Jumps)",
        line=dict(color="#00d4ff", width=2, dash="dash") # Neon blue dash
    ))

    # Merton Jump-Diffusion Curve (Highlighting Fat Tails)
    fig.add_trace(go.Scatter(
        x=x, y=pdf_merton, mode="lines",
        name="Merton Jump-Diffusion",
        line=dict(color="#a855f7", width=3), # QuantIV Purple
        fill="tozeroy",
        fillcolor="rgba(168, 85, 247, 0.15)" # Subtle purple glow under the curve
    ))

    fig.update_layout(
        title=dict(text="Distribution of Asset Prices at Expiry: BS vs Merton", font=dict(color="#E0E0E0", size=16)),
        xaxis_title="Asset Price at Expiry (₹)",
        yaxis_title="Probability Density",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False),
        legend=dict(x=0.02, y=0.98),
        hovermode="x unified"
    )
    
    # Add annotation explicitly pointing to the "Fat Tail"
    fig.add_annotation(
        x=60, y=0.006,
        text="Left 'Fat Tail'<br>(Real Crash Risk)",
        showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#f59e0b",
        font=dict(color="#f59e0b", size=12)
    )
    
    return fig
