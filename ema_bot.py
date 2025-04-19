import os
from dotenv import load_dotenv
from binance.um_futures import UMFutures

# Configuración
load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
client = UMFutures(api_key, api_secret, base_url="https://testnet.binancefuture.com")

symbol = "BTCUSDT"
leverage = 5

# Obtener balance USDT disponible
balance_data = client.balance()
usdt_balance = float([x for x in balance_data if x["asset"] == "USDT"][0]["balance"])

# Calcular capital operable
capital_operable = usdt_balance * leverage
print(f"💰 Balance disponible: {usdt_balance:.2f} USDT | Capital apalancado: {capital_operable:.2f} USDT")

# Obtener precio actual
price = float(client.ticker_price(symbol=symbol)["price"])
print(f"📈 Precio actual: {price} USDT")

# Calcular cantidad en BTC (redondeado a 3 decimales)
quantity = round(capital_operable / price, 3)

# Calcular los precios de TP y SL
tp_price = round(price * 1.01, 2)  # +1%
sl_price = round(price * 0.995, 2)  # -0.5%

# Ejecutar orden de mercado (long)
order = client.new_order(
    symbol=symbol,
    side="BUY",
    type="MARKET",
    quantity=quantity
)
print(f"✅ Orden de compra ejecutada: {quantity} BTC a {price} USDT")

# Colocar TP (limit sell) y SL (stop market sell)
# TP
client.new_order(
    symbol=symbol,
    side="SELL",
    type="TAKE_PROFIT_MARKET",
    stopPrice=str(tp_price),
    closePosition=True,
    timeInForce="GTC"
)

# SL
client.new_order(
    symbol=symbol,
    side="SELL",
    type="STOP_MARKET",
    stopPrice=str(sl_price),
    closePosition=True,
    timeInForce="GTC"
)

print(f"🎯 TP colocado en {tp_price} USDT | 🔴 SL colocado en {sl_price} USDT")
