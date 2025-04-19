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

while True:
    print("📉 Analizando el mercado...")
    print("🔌 Conectando a Binance Testnet...")

    try:
        klines = client.klines(symbol, "15m", limit=100)
        print(f"✅ Klines recibidas correctamente. Total: {len(klines)} velas")

        # Obtener precio actual
        price = float(client.ticker_price(symbol=symbol)["price"])
        quantity = round(0.03, 3)  # Fijo: 0.03 BTC

        # Ejecutar orden de compra
        print(f"🛒 Ejecutando orden de COMPRA por {quantity} BTC (~{round(price * quantity, 2)} USDT)")
        response = client.new_order(
            symbol=symbol,
            side="BUY",
            type="MARKET",
            quantity=quantity
        )
        print("✅ Orden ejecutada:", response["orderId"])

    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(5)
        continue

    print("⏳ Esperando 5 minutos...\n")
    time.sleep(5)
