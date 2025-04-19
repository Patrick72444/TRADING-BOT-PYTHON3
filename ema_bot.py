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

# Función para obtener el balance de USDT disponible
def get_usdt_balance():
    balances = client.balance()
    for b in balances:
        if b["asset"] == "USDT":
            return float(b["balance"])
    return 0.0

while True:
    print("📉 Analizando el mercado...")
    print("🔌 Conectando a Binance Testnet...")

    try:
        klines = client.klines(symbol, "15m", limit=100)
        print(f"✅ Klines recibidas correctamente. Total: {len(klines)} velas")
    except Exception as e:
        print(f"❌ Error al obtener klines: {e}")
        time.sleep(300)
        continue

    # Obtener balance actual y precio de mercado
    balance = get_usdt_balance()
    price = float(client.ticker_price(symbol=symbol)["price"])
    
    # Calcular la cantidad a comprar con el 100% del balance
    quantity = round(balance / price, 3)

    try:
        order = client.new_order(
            symbol=symbol,
            side="BUY",
            type="MARKET",
            quantity=quantity
        )
        print(f"✅ Ejecutando orden de COMPRA por {quantity} BTC (~{balance} USDT)")
    except Exception as e:
        print(f"❌ Error al colocar orden de compra: {e}")

    print("⏳ Esperando 5 minutos...\n")
    time.sleep(10)

