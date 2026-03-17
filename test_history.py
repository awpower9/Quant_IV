import sys
sys.path.append("c:\\QuantivFinal")
from quantiv.data.providers.yahoo import YahooFinanceProvider
yf = YahooFinanceProvider()
data = yf.get_intraday_history("TSLA", points=5)
print(f"Got {len(data)} points: {data}")
