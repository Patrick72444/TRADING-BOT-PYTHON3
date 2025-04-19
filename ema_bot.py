import os
from dotenv import load_dotenv
from binance.um_futures import UMFutures

# Cargar claves desde .env
load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
client = UMFutures(api_key, api_secret, base_url="https://testnet.binancefuture.com")

symbol = "BTCUSDT"

print("🔌 Conectando a Binance Testnet...")

# Obtener balance en USDT
balance_info = client.balance()
usdt_balance = next((float(b['balance']) for b in balance_info if b['asset'] == 'USDT'), 0.0)

# Obtener precio actual del BTC
price = float(client.ticker_price(symbol=symbol)["price"])

# Calcular cantidad de BTC a comprar (100% del balance)
quantity = round(usdt_balance / price, 3)
print(f"💰 Balance USDT: {usdt_balance:.2f} | Precio BTC: {price:.2f} | Cantidad: {quantity} BTC")

# Crear orden de compra
order = client.new_order(
    symbol=symbol,
    side="BUY",
    type="MARKET",
    quantity=quantity
)
print("✅ Orden de COMPRA ejecutada")

# Calcular valores de SL y TP
sl_price = round(price * 0.995, 2)  # -0.5%
tp_price = round(price * 1.01, 2)   # +1%

# Crear orden OCO para cerrar la operación con SL y TP
client.new_order(
    symbol=symbol,
    side="SELL",
    type="TAKE_PROFIT_MARKET",
    stopPrice=str(tp_price),
    closePosition=True
)
client.new_order(
    symbol=symbol,
    side="SELL",
    type="STOP_MARKET",
    stopPrice=str(sl_price),
    closePosition=True
)

print(f"🎯 TAKE PROFIT colocado en: {tp_price}")
print(f"🛑 STOP LOSS colocado en: {sl_price}")
