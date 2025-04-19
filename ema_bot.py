import os
import time
from dotenv import load_dotenv
from binance.um_futures import UMFutures

# Cargar claves desde .env
load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
client = UMFutures(api_key, api_secret, base_url="https://testnet.binancefuture.com")

symbol = "BTCUSDT"

def get_balance():
    balances = client.balance()
    for asset in balances:
        if asset["asset"] == "USDT":
            return float(asset["balance"])
    return 0.0

while True:
    print("📉 Analizando el mercado...")
    print("🔌 Conectando a Binance Testnet...")

    try:
        klines = client.klines(symbol, "15m", limit=100)
        print(f"✅ Klines recibidas correctamente. Total: {len(klines)} velas")
        
        usdt_balance = get_balance()
        price = float(client.ticker_price(symbol=symbol)["price"])
        qty = round(usdt_balance / price, 3)

        order = client.new_order(
            symbol=symbol,
            side="BUY",
            type="MARKET",
            quantity=qty
        )
        print(f"✅ Orden de COMPRA ejecutada con {qty} BTC (~{usdt_balance} USDT)")

    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(10)
        continue

    print("⏳ Esperando 5 minutos...\n")
    time.sleep(10)

