import os
import time
import pandas as pd
import pandas_ta as ta
from dotenv import load_dotenv
from binance.um_futures import UMFutures

# Configuración
load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
client = UMFutures(api_key, api_secret, base_url="https://testnet.binancefuture.com")

symbol = "BTCUSDT"
leverage = 5

# Establecer apalancamiento y margen aislado correctamente
try:
    positions = client.get_position_risk(symbol=symbol)
    if positions and isinstance(positions, list):
        current_margin_type = positions[0].get("marginType", "CROSSED")
        if current_margin_type != "ISOLATED":
            client.change_margin_type(symbol=symbol, marginType="ISOLATED")
            print("✅ Margen cambiado a ISOLATED")
        else:
            print("ℹ️ El margen ya es ISOLATED")
    else:
        print("⚠️ No se pudo obtener información de margen")

    client.change_leverage(symbol=symbol, leverage=leverage)
    print(f"✅ Apalancamiento configurado a x{leverage}")
except Exception as e:
    print(f"❌ Error al configurar margen/apalancamiento: {e}")

# Función para obtener el balance USDT actual
def get_usdt_balance():
    balances = client.balance()
    for b in balances:
        if b["asset"] == "USDT":
            return float(b["balance"])
    return 0.0

# Calcular EMAs manualmente
def calcular_ema(data, periodo):
    k = 2 / (periodo + 1)
    ema = [sum(data[:periodo]) / periodo]
    for precio in data[periodo:]:
        ema.append(precio * k + ema[-1] * (1 - k))
    return [None] * (periodo - 1) + ema

# Bucle principal
while True:
    print("📉 Analizando el mercado...")
    try:
        klines = client.klines(symbol, "15m", limit=100)
        closes = [float(k[4]) for k in klines]

        ema9 = calcular_ema(closes, 9)
        ema21 = calcular_ema(closes, 21)

        if True:
            print("🟢 Señal de COMPRA detectada")
            initial_balance = get_usdt_balance()
            price = float(client.ticker_price(symbol=symbol)["price"])
            capital_operable = initial_balance * leverage
            quantity = round(capital_operable * 0.95 / price, 3)

            order = client.new_order(symbol=symbol, side="BUY", type="MARKET", quantity=quantity)
            print(f"✅ Compra ejecutada. Balance inicial: {initial_balance:.2f} USDT")

            while True:
                current_balance = get_usdt_balance()
                diff = ((current_balance - initial_balance) / initial_balance) * 100
                print(f"📈 Variación de balance: {diff:.2f}%")

                if diff >= 3:
                    client.new_order(symbol=symbol, side="SELL", type="MARKET", quantity=quantity)
                    print("🎯 TAKE PROFIT alcanzado (+3% balance)")
                    break
                elif diff <= -1.5:
                    client.new_order(symbol=symbol, side="SELL", type="MARKET", quantity=quantity)
                    print("🔴 STOP LOSS alcanzado (-1.5% balance)")
                    break
                time.sleep(60)

        elif ema9[-2] > ema21[-2] and ema9[-1] < ema21[-1]:
            print("🔴 Señal de VENTA detectada")
            initial_balance = get_usdt_balance()
            price = float(client.ticker_price(symbol=symbol)["price"])
            capital_operable = initial_balance * leverage
            quantity = round(capital_operable / price, 4)

            order = client.new_order(symbol=symbol, side="SELL", type="MARKET", quantity=quantity)
            print(f"✅ Venta ejecutada. Balance inicial: {initial_balance:.2f} USDT")

            while True:
                current_balance = get_usdt_balance()
                diff = ((current_balance - initial_balance) / initial_balance) * 100
                print(f"📉 Variación de balance: {diff:.2f}%")

                if diff >= 3:
                    client.new_order(symbol=symbol, side="BUY", type="MARKET", quantity=quantity)
                    print("🎯 TAKE PROFIT alcanzado (+3% balance)")
                    break
                elif diff <= -1.5:
                    client.new_order(symbol=symbol, side="BUY", type="MARKET", quantity=quantity)
                    print("🔴 STOP LOSS alcanzado (-1.5% balance)")
                    break
                time.sleep(60)

        else:
            print("⚪ Sin señal clara")

    except Exception as e:
        print("❌ Error en ejecución:", e)

    print("⏳ Esperando 5 minutos...")
    time.sleep(300)

from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot funcionando..."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
