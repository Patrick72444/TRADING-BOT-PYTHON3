import os
from dotenv import load_dotenv
from binance.um_futures import UMFutures

# Cargar claves desde .env
load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
client = UMFutures(api_key, api_secret, base_url="https://testnet.binancefuture.com")

# Parámetros
symbol = "BTCUSDT"
quantity_btc = 0.03
leverage = 5

# Establecer apalancamiento
try:
    client.change_leverage(symbol=symbol, leverage=leverage)
    print(f"✅ Apalancamiento establecido a x{leverage}")
except Exception as e:
    print(f"❌ Error al establecer apalancamiento: {e}")

# Obtener precio actual
price_data = client.ticker_price(symbol=symbol)
entry_price = float(price_data["price"])
print(f"💰 Precio de entrada: {entry_price} USDT")

# Calcular SL y TP
take_profit_price = round(entry_price * (1 + 0.0075), 2)  # +0.75%
stop_loss_price = round(entry_price * (1 - 0.003), 2)     # -0.3%

print(f"🎯 TP en: {take_profit_price} USDT")
print(f"🛑 SL en: {stop_loss_price} USDT")

# Ejecutar orden de compra
try:
    order = client.new_order(
        symbol=symbol,
        side="BUY",
        type="MARKET",
        quantity=quantity_btc
    )
    print(f"✅ Orden de COMPRA ejecutada: {order}")
except Exception as e:
    print(f"❌ Error al ejecutar orden de compra: {e}")
    exit()

# Colocar TP y SL
try:
    # Take Profit
    tp_order = client.new_order(
        symbol=symbol,
        side="SELL",
        type="LIMIT",
        quantity=quantity_btc,
        price=str(take_profit_price),
        timeInForce="GTC"
    )
    print(f"🎯 TP colocado en {take_profit_price}")

    # Stop Loss
    sl_order = client.new_order(
        symbol=symbol,
        side="SELL",
        type="STOP_MARKET",
        stopPrice=str(stop_loss_price),
        closePosition=True,
        timeInForce="GTC"
    )
    print(f"🛑 SL colocado en {stop_loss_price}")
except Exception as e:
    print(f"❌ Error al colocar TP/SL: {e}")
