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
fixed_quantity = 0.03  # Cantidad fija de BTC por operación

# Calcular EMAs manualmente
def calcular_ema(data, periodo):
    k = 2 / (periodo + 1)
    ema = [sum(data[:periodo]) / periodo]
    for precio in data[periodo:]:
        ema.append(precio * k + ema[-1] * (1 - k))
    return [None] * (periodo - 1) + ema

# Función para obtener el balance USDT actual
def get_usdt_balance():
    balances = client.balance()
    for b in balances:
        if b["asset"] == "USDT":
            return float(b["balance"])
    return 0.0

# Bucle principal
while True:
    print("📉 Analizando el mercado...")
    try:
        klines = client.klines(symbol, "15m", limit=100)
        closes = [float(k[4]) for k in klines]

        ema9 = calcular_ema(closes, 9)
        ema21 = calcular_ema(closes, 21)

        if ema9[-2] < ema21[-2] and ema9[-1] > ema21[-1]:
            print("🟢 Señal de COMPRA detectada")
            initial_balance = get_usdt_balance()
            client.new_order(symbol=symbol, side="BUY", type="MARKET", quantity=fixed_quantity)
            print(f"✅ Orden de COMPRA ejecutada por {fixed_quantity} BTC")

            while True:
                current_balance = get_usdt_balance()
                diff = ((current_balance - initial_balance) / initial_balance) * 100
                print(f"📈 Variación de balance: {diff:.2f}%")

                if diff >= 3:
                    client.new_order(symbol=symbol, side="SELL", type="MARKET", quantity=fixed_quantity)
                    print("🎯 TAKE PROFIT alcanzado (+3%)")
                    break
                elif diff <= -1.5:
                    client.new_order(symbol=symbol, side="SELL", type="MARKET", quantity=fixed_quantity)
                    print("🔴 STOP LOSS alcanzado (-1.5%)")
                    break
                time.sleep(60)

        elif ema9[-2] > ema21[-2] and ema9[-1] < ema21[-1]:
            print("🔴 Señal de VENTA detectada")
            initial_balance = get_usdt_balance()
            client.new_order(symbol=symbol, side="SELL", type="MARKET", quantity=fixed_quantity)
            print(f"✅ Orden de VENTA ejecutada por {fixed_quantity} BTC")

            while True:
                current_balance = get_usdt_balance()
                diff = ((current_balance - initial_balance) / initial_balance) * 100
                print(f"📉 Variación de balance: {diff:.2f}%")

                if diff >= 3:
                    client.new_order(symbol=symbol, side="BUY", type="MARKET", quantity=fixed_quantity)
                    print("🎯 TAKE PROFIT alcanzado (+3%)")
                    break
                elif diff <= -1.5:
                    client.new_order(symbol=symbol, side="BUY", type="MARKET", quantity=fixed_quantity)
                    print("🔴 STOP LOSS alcanzado (-1.5%)")
                    break
                time.sleep(60)
        else:
            print("⚪ Sin señal clara")

    except Exception as e:
        print("❌ Error en ejecución:", e)

    print("⏳ Esperando 5 minutos antes de volver a analizar...")
    time.sleep(300)
