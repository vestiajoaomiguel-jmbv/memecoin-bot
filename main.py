
import os
import time
import requests
from collections import defaultdict
from telegram import Bot
import asyncio

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/pairs/solana"
SOLSCAN_API = "https://public-api.solscan.io/token/holders"

bot = Bot(token=TELEGRAM_TOKEN)

seen_tokens = set()
history = defaultdict(lambda: {"volume": 0, "traders": 0})

def get_pairs():
    url = "https://api.dexscreener.com/token-profiles/latest/v1"
    r = requests.get(url, timeout=20)
    if r.status_code != 200:
        return []
    return r.json()

def get_solscan_data(token_address):
    try:
        headers = {"accept": "application/json"}
        r = requests.get(
            f"https://public-api.solscan.io/token/meta?tokenAddress={token_address}",
            headers=headers,
            timeout=20
        )

        if r.status_code != 200:
            return None

        data = r.json()

        holders = data.get("holder", 0)
        top10 = data.get("top10HolderPercent", 100)

        return {
            "holders": holders,
            "top10": top10
        }

    except Exception:
        return None

def classify(score):
    if score >= 8:
        return "A+"
    elif score >= 5:
        return "B"
    return "C"

def analyze_pair(pair):
    try:
        liquidity = pair.get("liquidity", {}).get("usd", 0)
        mc = pair.get("fdv", 0)

        volume_1h = pair.get("volume", {}).get("h1", 0)
        txns = pair.get("txns", {}).get("h1", {})
        buys = txns.get("buys", 0)
        sells = txns.get("sells", 0)
        txns_total = buys + sells

        age_hours = 999

        if pair.get("pairCreatedAt"):
            age_hours = (time.time() * 1000 - pair["pairCreatedAt"]) / 3600000

        token_address = pair.get("baseToken", {}).get("address")
        symbol = pair.get("baseToken", {}).get("symbol", "???")
        price = pair.get("priceUsd", "0")

        if not token_address:
            return None

        solscan = get_solscan_data(token_address)

        if not solscan:
            return None

        holders = solscan["holders"]
        top10 = solscan["top10"]

        score = 0

        if liquidity > 150000:
            score += 1

        if 90000 <= mc <= 5000000:
            score += 1

        if age_hours < 24:
            score += 1

        if volume_1h > 50000:
            score += 1

        if txns_total > 300:
            score += 1

        if top10 < 25:
            score += 1

        if holders > 300:
            score += 1

        prev_volume = history[token_address]["volume"]
        prev_traders = history[token_address]["traders"]

        traders_now = buys + sells

        if volume_1h > prev_volume:
            score += 1

        if traders_now > prev_traders:
            score += 1

        netflow = buys - sells

        if netflow > 0:
            score += 1

        history[token_address]["volume"] = volume_1h
        history[token_address]["traders"] = traders_now

        classification = classify(score)

        return {
            "symbol": symbol,
            "address": token_address,
            "price": price,
            "liquidity": liquidity,
            "mc": mc,
            "volume_1h": volume_1h,
            "txns": txns_total,
            "holders": holders,
            "top10": top10,
            "netflow": netflow,
            "classification": classification,
            "score": score
        }

    except Exception as e:
        print("Erro:", e)
        return None

async def send_alert(token):
    message = f"""
🚨 MEMECOIN ALERTA

Token: {token['symbol']}
Classificação: {token['classification']}
Score: {token['score']}/10

💧 Liquidity: ${token['liquidity']:,.0f}
🏦 Market Cap: ${token['mc']:,.0f}
📈 Volume 1h: ${token['volume_1h']:,.0f}
🔄 Txns 1h: {token['txns']}
👥 Holders: {token['holders']}
🐋 Top 10: {token['top10']}%
🟢 Net Flow: {token['netflow']}

📍 CA:
{token['address']}

🔎 DexScreener:
https://dexscreener.com/solana/{token['address']}
"""

    await bot.send_message(chat_id=CHAT_ID, text=message)

def run():
    print("Bot iniciado...")

    while True:
        try:
            pairs = get_pairs()

            for pair in pairs:
                token = analyze_pair(pair)

                if not token:
                    continue

                address = token["address"]

                if token["classification"] == "A+" and address not in seen_tokens:
                    asyncio.run (send_alert(token))
                    seen_tokens.add(address)

            time.sleep(60)

        except Exception as e:
            print("Loop error:", e)
            time.sleep(30)

if __name__ == "__main__":
    run()
