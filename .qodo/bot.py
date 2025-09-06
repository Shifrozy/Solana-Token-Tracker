import os
import time
import requests
from dotenv import load_dotenv
from telegram import Bot

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("BOT_TOKEN or CHAT_ID missing in .env")

CHAT_ID = int(CHAT_ID)
bot = Bot(token=BOT_TOKEN)

seen_tokens = set()

def check_new_tokens():
    url = "https://api.dexscreener.com/token-profiles/latest/v1"
    try:
        resp = requests.get(url, timeout=10)
    except requests.RequestException as e:
        print("Request failed:", e)
        return

    if resp.status_code != 200:
        print("API error:", resp.status_code, resp.text[:200])
        return

    try:
        data = resp.json()
    except ValueError as e:
        print("JSON decode error:", e)
        print("Response text:", resp.text[:200])
        return

    # The response may be a list or object — adapt accordingly
    token_items = data if isinstance(data, list) else data.get("tokenProfiles", data.get("profiles", []))
    if not token_items:
        print("No token profiles returned.")
        return

    for item in token_items:
        addr = item.get("tokenAddress")
        if not addr or addr in seen_tokens:
            continue

        seen_tokens.add(addr)
        name = item.get("header") or "Unknown"
        url_token = item.get("url", "")
        msg = (
            f"🚀 *New Solana Token Profile Detected!*\n\n"
            f"🆔 Address: `{addr}`\n"
            f"🏷 Name: *{name}*\n"
            f"🔗 [View Token]({url_token})"
        )
        try:
            bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
            print("Alerted:", name, addr)
        except Exception as e:
            print("Telegram send failed:", e)

if __name__ == "__main__":
    print("Starting Solana Token Tracker (using token profiles)...")
    while True:
        check_new_tokens()
        time.sleep(60)
