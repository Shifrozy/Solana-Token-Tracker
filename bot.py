import os
import time
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Track seen tokens
seen_tokens = set()
AGE_FILTER = None   # set by user input
CHAIN = None        # set by user input (e.g., solana, ethereum, bsc)


# -------------------------------
# Telegram Bot Handlers
# -------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "First, choose which chain you want to monitor.\n"
        "Example: send `solana`, `ethereum`, or `bsc`.\n\n"
        "After that, enter how many hours old tokens you want (e.g., 24, 72, 168)."
    )


async def set_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global AGE_FILTER, CHAIN
    text = update.message.text.strip().lower()

    # Step 1: Set chain
    if text in ["solana", "ethereum", "bsc"]:
        CHAIN = text
        await update.message.reply_text(f"✅ Chain set to: {CHAIN.capitalize()}")
        return

    # Step 2: Set age filter
    try:
        hours = int(text)
        if hours <= 0:
            raise ValueError
        AGE_FILTER = hours
        await update.message.reply_text(
            f"✅ Age filter set: tracking tokens ≤ {AGE_FILTER} hours old."
        )
    except ValueError:
        await update.message.reply_text(
            "⚠️ Please enter either:\n"
            "- A valid chain name (`solana`, `ethereum`, `bsc`)\n"
            "- Or a number of hours (24, 72, 168)"
        )


# -------------------------------
# DexScreener Token Fetch
# -------------------------------

def fetch_tokens():
    if not CHAIN:
        return []

    url = f"https://api.dexscreener.com/latest/dex/search?q={CHAIN}"
    response = requests.get(url)
    if response.status_code != 200:
        print("❌ API error:", response.text)
        return []
    return response.json().get("pairs", [])


async def check_new_tokens(context: ContextTypes.DEFAULT_TYPE):
    global seen_tokens, AGE_FILTER, CHAIN
    if AGE_FILTER is None or CHAIN is None:
        # Skip if user hasn't set chain and filter yet
        return

    pairs = fetch_tokens()
    if not pairs:
        return

    now = time.time()

    for pair in pairs:
        token_address = pair["baseToken"]["address"]
        created_at = pair.get("pairCreatedAt")  # reliable field in ms

        # Skip if already seen
        if token_address in seen_tokens:
            continue

        # Apply age filter
        token_age_hours = None
        if created_at:
            token_age_hours = (now - (created_at / 1000)) / 3600
            if token_age_hours > AGE_FILTER:
                continue

        seen_tokens.add(token_address)

        # Detect chain (for display)
        chain = pair.get("chainId", "Unknown").capitalize()

        name = pair["baseToken"]["name"]
        symbol = pair["baseToken"]["symbol"]
        url = pair["url"]

        message = (
            f"🚀 <b>New {chain} Pair Detected!</b>\n\n"
            f"<b>Name:</b> {name}\n"
            f"<b>Symbol:</b> {symbol}\n"
        )

        if token_age_hours is not None:
            message += f"<b>Age:</b> {round(token_age_hours, 2)} hours\n"

        message += f"<b>Chart:</b> {url}"

        await context.bot.send_message(
            chat_id=CHAT_ID, text=message, parse_mode="HTML"
        )
        print("✅ Alert sent:", name, symbol, f"({chain})")


# -------------------------------
# Main Runner
# -------------------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_user_input))

    # Faster background job → check every 15 seconds
    app.job_queue.run_repeating(check_new_tokens, interval=15, first=5)

    print("🤖 Bot started! Waiting for user to set chain + age filter...")
    app.run_polling()


if __name__ == "__main__":
    main()
