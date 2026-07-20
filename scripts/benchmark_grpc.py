import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dashboard.grpc_client import QuantivGrpcClient

def run_benchmark():
    client = QuantivGrpcClient()
    spot = 100.0
    strike = 100.0
    vol = 0.2
    rate = 0.05
    expiry = 1.0
    is_call = True
    
    num_iters = 10000
    
    # 1. Black Scholes
    start = time.perf_counter()
    for _ in range(num_iters):
        client.price_black_scholes(spot, strike, vol, rate, expiry, is_call)
    end = time.perf_counter()
    bsm_time = end - start
    print(f"Black Scholes: {num_iters} prices in {bsm_time:.4f}s -> {num_iters/bsm_time:.0f} prices/sec")
    
    # 2. Binomial (100 steps)
    start = time.perf_counter()
    for _ in range(num_iters):
        client.price_binomial(spot, strike, vol, rate, expiry, is_call, 100)
    end = time.perf_counter()
    bin_time = end - start
    print(f"Binomial (100 steps): {num_iters} prices in {bin_time:.4f}s -> {num_iters/bin_time:.0f} prices/sec")

    # 3. Monte Carlo (5000 paths)
    start = time.perf_counter()
    # reduce iterations for MC so it doesn't take forever if it's slow
    mc_iters = 1000
    for _ in range(mc_iters):
        client.price_monte_carlo(spot, strike, vol, rate, expiry, is_call, 5000)
    end = time.perf_counter()
    mc_time = end - start
    print(f"Monte Carlo (5000 paths): {mc_iters} prices in {mc_time:.4f}s -> {mc_iters/mc_time:.0f} prices/sec")

    # 4. Heston
    start = time.perf_counter()
    for _ in range(num_iters):
        client.price_heston(spot, strike, vol, rate, expiry, is_call, 2.0, 0.04, 0.3, -0.7)
    end = time.perf_counter()
    heston_time = end - start
    print(f"Heston: {num_iters} prices in {heston_time:.4f}s -> {num_iters/heston_time:.0f} prices/sec")

if __name__ == "__main__":
    print("Starting gRPC Benchmark...")
    run_benchmark()
