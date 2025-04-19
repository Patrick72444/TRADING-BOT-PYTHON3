import os
import time
import pandas as pd
from dotenv import load_dotenv
from binance.um_futures import UMFutures

# Configuración
load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
client = UMFutures(api_key, api_secret, base_url="https://testnet.binancefuture.com")

symbol = "BTCUSDT"
leverage = 5

def log(msg):
    print(f"[LOG] {msg}")

# Configurar apalancamiento y margen aislado
try:
    positions = client.get_position_risk(symbol=symbol)
    if positions and isinstance(positions, list):
        current_margin_type = positions[0].get("marginType", "CROSSED")
        if current_margin_type != "ISOLATED":
            client.change_margin_type(symbol=symbol, marginType="ISOLATED")
            log("✅ Margen cambiado a ISOLATED")
        else:
            log("ℹ️ El margen ya es ISOLATED")
    else:
        log("⚠️ No se pudo obtener información de margen")

    client.change_leverage(symbol=symbol, leverage=leverage)
    log(f"✅ Apalancamiento configurado a x{leverage}")
except Exception as e:
    log(f"❌ Error al configurar margen/apalancamiento: {e}")

def get_usdt_balance():
    try:
        balances = client.balance()
        for b in balances:
            if b["asset"] == "USDT":
                return float(b["balance"])
    except Exception as e:
        log(f"❌ Error al obtener balance: {e}")
    return 0.0

def calcular_ema(data, periodo):
    k = 2 / (periodo + 1)
    ema = [sum(data[:periodo]) / periodo]
    for precio in data[periodo:]:
        ema.append(precio * k + ema[-1] * (1 - k))
    return [None] * (periodo - 1) + ema

# Bucle principal
while True:
    try:
        log("📉 Analizando el mercado...")
        klines = client.klines(symbol, "15m", limit=100)
        closes = [float(k[4]) for k in klines]

        ema9 = calcular_ema(closes, 9)
        ema21 = calcular_ema(closes, 21)

        if ema9[-2] < ema21[-2] and ema9[-1] > ema21[-1]:
            log("🟢 Señal de COMPRA detectada")
            initial_balance = get_usdt_balance()
            price = float(client.ticker_price(symbol=symbol)["price"])
            quantity = round((initial_balance * leverage * 0.95) / price, 3)

            order = client.new_order(symbol=symbol, side="BUY", type="MARKET", quantity=quantity)
            log(f"✅ Compra ejecutada. Precio: {price}, Cantidad: {quantity}, Balance inicial: {initial_balance:.2f}")

            while True:
                current_balance = get_usdt_balance()
                diff = ((current_balance - initial_balance) / initial_balance) * 100
                log(f"📈 Variación balance: {diff:.2f}%")

                if diff >= 3:
                    client.new_order(symbol=symbol, side="SELL", type="MARKET", quantity=quantity)
                    log("🎯 TAKE PROFIT alcanzado (+3%)")
                    break
                elif diff <= -1.5:
                    client.new_order(symbol=symbol, side="SELL", type="MARKET", quantity=quantity)
                    log("🔴 STOP LOSS alcanzado (-1.5%)")
                    break
                time.sleep(60)

        elif ema9[-2] > ema21[-2] and ema9[-1] < ema21[-1]:
            log("🔴 Señal de VENTA detectada")
            initial_balance = get_usdt_balance()
            price = float(client.ticker_price(symbol=symbol)["price"])
            quantity = round((initial_balance * leverage * 0.95) / price, 3)

            order = client.new_order(symbol=symbol, side="SELL", type="MARKET", quantity=quantity)
            log(f"✅ Venta ejecutada. Precio: {price}, Cantidad: {quantity}, Balance inicial: {initial_balance:.2f}")

            while True:
                current_balance = get_usdt_balance()
                diff = ((current_balance - initial_balance) / initial_balance) * 100
                log(f"📉 Variación balance: {diff:.2f}%")

                if diff >= 3:
                    client.new_order(symbol=symbol, side="BUY", type="MARKET", quantity=quantity)
                    log("🎯 TAKE PROFIT alcanzado (+3%)")
                    break
                elif diff <= -1.5:
                    client.new_order(symbol=symbol, side="BUY", type="MARKET", quantity=quantity)
                    log("🔴 STOP LOSS alcanzado (-1.5%)")
                    break
                time.sleep(60)

        else:
            log("⚪ Sin señal clara")
    except Exception as e:
        log(f"❌ Error general: {e}")

    log("⏳ Esperando 5 minutos antes de volver a analizar...")
    time.sleep(300)

