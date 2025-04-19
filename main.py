import os
from binance.um_futures import UMFutures
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

client = UMFutures(api_key, api_secret, base_url="https://testnet.binancefuture.com")

price = client.ticker_price(symbol="BTCUSDT")
print(f"Precio actual BTCUSDT: {price['price']}")
