import numpy as np
from scipy.stats import norm
import argparse

def black_scholes_call(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

def black_scholes_put(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

def black_scholes_vega(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    return S * norm.pdf(d1) * np.sqrt(T)

def implied_volatility_educational(target_price, S, K, T, r, is_call=True):
    """
    Calculates Implied Volatility using Newton-Raphson and tracks convergence steps.
    Returns: (final_iv, list_of_steps_dict)
    """
    MAX_VOL = 5.0
    MIN_VOL = 1e-4
    MAX_ITER = 50
    TOL = 1e-6

    # Arbitrage bounds check
    if is_call:
        if target_price <= max(0, S - K * np.exp(-r * T)) or target_price >= S:
            raise ValueError("Target price violates arbitrage bounds for Call option.")
    else:
        if target_price <= max(0, K * np.exp(-r * T) - S) or target_price >= K:
            raise ValueError("Target price violates arbitrage bounds for Put option.")

    # Brenner-Subrahmanyam approximation for initial guess
    sigma = np.sqrt(2 * np.pi / T) * (target_price / S)
    sigma = np.clip(sigma, 0.05, 3.0)

    steps = []

    for i in range(MAX_ITER):
        if is_call:
            price = black_scholes_call(S, K, T, r, sigma)
        else:
            price = black_scholes_put(S, K, T, r, sigma)
            
        diff = price - target_price
        steps.append({"iteration": i, "sigma": sigma, "price": price, "error": diff})
        
        if abs(diff) < TOL:
            return sigma, steps
            
        vega = black_scholes_vega(S, K, T, r, sigma)
        
        if vega < 1e-8:
            # Fallback
            sigma += -0.01 if diff > 0 else 0.01
        else:
            # Newton step
            sigma = sigma - diff / vega
            
        sigma = np.clip(sigma, MIN_VOL, MAX_VOL)
        
    raise ValueError("Implied volatility did not converge.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--spot", type=float, default=450.0)
    parser.add_argument("--strike", type=float, default=455.0)
    parser.add_argument("--expiry", type=float, default=0.25)
    parser.add_argument("--rate", type=float, default=0.05)
    parser.add_argument("--price", type=float, default=12.50)
    parser.add_argument("--put", action="store_true")
    args = parser.parse_args()

    try:
        iv, steps = implied_volatility_educational(args.price, args.spot, args.strike, args.expiry, args.rate, not args.put)
        print(f"IV: {iv:.6f}")
        for step in steps:
            print(f"Step {step['iteration']}: Vol={step['sigma']:.4f}, Price={step['price']:.4f}, Error={step['error']:.6f}")
    except Exception as e:
        print(f"Error: {e}")

