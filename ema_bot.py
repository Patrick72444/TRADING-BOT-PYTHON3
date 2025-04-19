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
    except Exception as e:
        print(f"❌ Error al obtener klines: {e}")
        time.sleep(300)
        continue

    print("⏳ Esperando 5 minutos...\n")
    time.sleep(300)
