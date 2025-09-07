import os
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Telegram send function
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, data=payload)

# Track seen tokens
seen_tokens = set()

def check_new_tokens():
    url = "https://api.dexscreener.com/latest/dex/search?q=solana"
    response = requests.get(url)
    if response.status_code != 200:
        print("❌ API error:", response.text)
        return

    data = response.json()
    if "pairs" not in data:
        print("⚠️ No pairs found in response")
        return

    for pair in data["pairs"]:
        token_address = pair["baseToken"]["address"]
        if token_address not in seen_tokens:
            seen_tokens.add(token_address)

            # Create alert message
            name = pair["baseToken"]["name"]
            symbol = pair["baseToken"]["symbol"]
            url = pair["url"]

            message = f"🚀 <b>New Solana Token Detected!</b>\n\n" \
                      f"<b>Name:</b> {name}\n" \
                      f"<b>Symbol:</b> {symbol}\n" \
                      f"<b>Chart:</b> {url}"

            send_telegram_message(message)
            print("✅ Alert sent:", name, symbol)

if __name__ == "__main__":
    send_telegram_message("🤖 Bot started! Now watching for new Solana tokens...")
    while True:
        check_new_tokens()
        time.sleep(60)  # check every 60s
