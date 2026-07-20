from quantiv.pricing.pricer import Pricer
from scripts.calculate_iv import implied_volatility_educational

print("Testing Pricer instantiation...")
pricer = Pricer()
models = ["bsm", "binomial", "trinomial", "monte_carlo"]

target_price = 10.0
spot = 100.0
strike = 100.0
expiry = 1.0
rate = 0.05
is_call = True
option_type = "call"

try:
    print("Testing IV...")
    iv, steps = implied_volatility_educational(target_price, spot, strike, expiry, rate, is_call)
    print(f"IV: {iv}")
    for m in models:
        try:
            print(f"Pricing {m}...")
            res = pricer.price(m, spot, strike, iv, rate, expiry, option_type, steps=100, num_paths=5000)
            diff = res.price - target_price
            print(f"{m} successful: {res.price}")
        except Exception as e:
            print(f"{m} failed: {e}")
            raise e
except Exception as e:
    print(f"Overall failed: {e}")
    raise e
