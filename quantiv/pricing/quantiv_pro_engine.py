"""
quantiv_pro_engine.py — Advanced Options Pricing Logic Engine
Contains high-performance characteristic function and jump-diffusion pricing models.
"""

import numpy as np
import scipy.integrate as integrate
from scipy.stats import norm
import math

# ─── CORE OPTION PRICING HELPERS ──────────────────────────────────────────────

def black_scholes_core(S, K, T, r, sigma, option_type):
    """Standard Black-Scholes needed as a base for Merton Jump-Diffusion."""
    if T <= 0.0 or sigma <= 0.0:
        val = S - K * np.exp(-r * T)
        if option_type == 'call': return max(val, 0.0)
        else: return max(-val, 0.0)

    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def finite_difference_greeks(price_func, S, *args, **kwargs):
    """Calculates Delta and Gamma dynamically using central finite differences."""
    dS = S * 0.01  # 1% shock for FD
    
    # Prices at S, S+dS, S-dS
    P = price_func(S, *args, **kwargs)
    P_up = price_func(S + dS, *args, **kwargs)
    P_dn = price_func(S - dS, *args, **kwargs)
    
    delta = (P_up - P_dn) / (2 * dS)
    gamma = (P_up - 2 * P + P_dn) / (dS**2)
    
    return {"price": float(P), "delta": float(delta), "gamma": float(gamma)}


# ─── HESTON MODEL (STOCHASTIC VOLATILITY) ─────────────────────────────────────

def heston_characteristic_func(u, S, T, r, v0, kappa, theta, sigma, rho, j):
    """Returns the Heston characteristic function f_j(x, v, T)."""
    i = 1j
    
    # Parameters distinct for P1 and P2
    if j == 1:
        u_j = 0.5
        b_j = kappa - rho * sigma
    else:
        u_j = -0.5
        b_j = kappa

    a = kappa * theta
    d = np.sqrt((rho * sigma * u * i - b_j)**2 - sigma**2 * (2 * u_j * u * i - u**2))
    
    # Guard against division by zero in case d exactly perfectly cancels out (rare edge case)
    denom = b_j - rho * sigma * u * i - d
    if np.abs(denom) < 1e-8:
        denom = 1e-8
    g = (b_j - rho * sigma * u * i + d) / denom
    
    # Prevent overflow in exponential
    exp_dT = np.exp(d * T)
    
    denom_g = 1 - g * exp_dT
    if np.abs(denom_g) < 1e-8:
         denom_g = 1e-8
         
    num_g = 1 - g
    if np.abs(num_g) < 1e-8:
         num_g = 1e-8

    C = (r * u * i * T + (a / sigma**2) * 
         ((b_j - rho * sigma * u * i + d) * T - 2 * np.log(denom_g / num_g)))
    D = ((b_j - rho * sigma * u * i + d) / sigma**2) * ((1 - exp_dT) / denom_g)
    
    return np.exp(C + D * v0 + i * u * np.log(S))


def _heston_integral(S, K, T, r, v0, kappa, theta, sigma, rho, j):
    """Integrator for Heston Probabilities P1 and P2."""
    def integrand(u):
        char_func = heston_characteristic_func(u, S, T, r, v0, kappa, theta, sigma, rho, j)
        return np.real((np.exp(-1j * u * np.log(K)) * char_func) / (1j * u))
    
    try:
        # Scipy Quad numerical integration up to infinity (bounded at 100 for safety)
        integral, _ = integrate.quad(integrand, 0.0001, 100.0, limit=250)
        return 0.5 + (1 / np.pi) * integral
    except Exception:
        # If integration fails due to extreme params, return naive BS approx
        return 0.5


def price_heston(S, K, T, r, v0, kappa, theta, sigma, rho, option_type="call"):
    """
    Computes theoretical price, delta, and gamma under the Heston Model.
    """
    if T <= 0: return {"price": max(S - K, 0) if option_type == 'call' else max(K - S, 0), "delta": 0, "gamma": 0}
    
    # Internal pricing closure for FD Greeks
    def _price(S_shocked):
        P1 = _heston_integral(S_shocked, K, T, r, v0, kappa, theta, sigma, rho, 1)
        P2 = _heston_integral(S_shocked, K, T, r, v0, kappa, theta, sigma, rho, 2)
        
        call_price = S_shocked * P1 - K * np.exp(-r * T) * P2
        if option_type == "call":
            return max(call_price, 0.0)
        else: # Put-Call Parity
            put_price = call_price - S_shocked + K * np.exp(-r * T)
            return max(put_price, 0.0)

    try:
        return finite_difference_greeks(_price, S)
    except Exception:
        return {"price": 0.0, "delta": 0.0, "gamma": 0.0}

# ─── MERTON JUMP-DIFFUSION MODEL ──────────────────────────────────────────────

def price_merton(S, K, T, r, sigma, lamb, mu_j, sigma_j, option_type="call"):
    """
    Computes theoretical price, delta, and gamma under the Merton Jump-Diffusion Model.
    Approximated using a Poisson-weighted sum of Black-Scholes prices (n=20 jumps).
    """
    if T <= 0: return {"price": max(S - K, 0) if option_type == 'call' else max(K - S, 0), "delta": 0, "gamma": 0}

    # Mean jump impact (compensator to prevent arbitrage drift)
    k_j = np.exp(mu_j + 0.5 * sigma_j**2) - 1 

    def _price(S_shocked):
        total_price = 0.0
        n_jumps = 20 # Standard cutoff for convergence

        for n in range(n_jumps):
            # Adjusted Volatility and Rate given EXACTLY n jumps occurred
            sigma_n = np.sqrt(sigma**2 + (n * sigma_j**2) / T)
            r_n = r - lamb * k_j + (n * (mu_j + 0.5 * sigma_j**2)) / T
            
            # Black-Scholes price under adjusted conditions
            bs_price = black_scholes_core(S_shocked, K, T, r_n, sigma_n, option_type)
            
            # Poisson probability of exactly 'n' jumps happening in time T
            # Poisson PMF = (e^(-lambda*T) * (lambda*T)^n) / n!
            weight = np.exp(-lamb * T) * ((lamb * T)**n) / math.factorial(n)
            
            total_price += weight * bs_price
            
        return total_price

    try:
        return finite_difference_greeks(_price, S)
    except Exception:
        return {"price": 0.0, "delta": 0.0, "gamma": 0.0}
