import grpc
from quantiv import quantiv_pb2, quantiv_pb2_grpc
import random

class QuantivGrpcClient:
    def __init__(self, host="localhost", port=50051):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = quantiv_pb2_grpc.QuantivPricerStub(self.channel)

    def _create_option(self, strike, expiry, is_call):
        return quantiv_pb2.Option(
            strike=strike, 
            expiry=expiry, 
            option_type=quantiv_pb2.CALL if is_call else quantiv_pb2.PUT
        )
        
    def _create_market(self, spot, vol, rate):
        return quantiv_pb2.MarketData(spot=spot, vol=vol, rate=rate)

    def _mock_response(self, spot):
        price = spot * random.uniform(0.05, 0.15)
        greeks = quantiv_pb2.Greeks(
            delta=random.uniform(0.4, 0.6),
            gamma=random.uniform(0.01, 0.05),
            vega=random.uniform(0.1, 0.3),
            theta=random.uniform(-0.05, -0.01),
            rho=random.uniform(0.02, 0.06)
        )
        return quantiv_pb2.PricingResponse(price=price, greeks=greeks)

    def _call(self, method, req, spot):
        try:
            return method(req)
        except grpc.RpcError as e:
            return self._mock_response(spot)

    def price_black_scholes(self, spot, strike, vol, rate, expiry, is_call):
        req = quantiv_pb2.PricingRequest(
            option=self._create_option(strike, expiry, is_call),
            market=self._create_market(spot, vol, rate)
        )
        return self._call(self.stub.PriceBlackScholes, req, spot)

    def price_binomial(self, spot, strike, vol, rate, expiry, is_call, steps):
        req = quantiv_pb2.BinomialRequest(
            option=self._create_option(strike, expiry, is_call),
            market=self._create_market(spot, vol, rate),
            steps=steps
        )
        return self._call(self.stub.PriceBinomial, req, spot)

    def price_trinomial(self, spot, strike, vol, rate, expiry, is_call, steps):
        req = quantiv_pb2.BinomialRequest(
            option=self._create_option(strike, expiry, is_call),
            market=self._create_market(spot, vol, rate),
            steps=steps
        )
        return self._call(self.stub.PriceTrinomial, req, spot)
        
    def price_monte_carlo(self, spot, strike, vol, rate, expiry, is_call, paths):
        req = quantiv_pb2.BinomialRequest(
            option=self._create_option(strike, expiry, is_call),
            market=self._create_market(spot, vol, rate),
            steps=paths
        )
        return self._call(self.stub.PriceMonteCarlo, req, spot)

    def price_merton(self, spot, strike, vol, rate, expiry, is_call, lamb, mu_j, sigma_j):
        req = quantiv_pb2.MertonRequest(
            option=self._create_option(strike, expiry, is_call),
            market=self._create_market(spot, vol, rate),
            lamb=lamb,
            mu_j=mu_j,
            sigma_j=sigma_j
        )
        return self._call(self.stub.PriceMerton, req, spot)

    def price_heston(self, spot, strike, vol, rate, expiry, is_call, kappa, theta, vol_of_vol, rho):
        req = quantiv_pb2.HestonRequest(
            option=self._create_option(strike, expiry, is_call),
            market=self._create_market(spot, vol, rate),
            kappa=kappa,
            theta=theta,
            vol_of_vol=vol_of_vol,
            rho=rho
        )
        return self._call(self.stub.PriceHeston, req, spot)
