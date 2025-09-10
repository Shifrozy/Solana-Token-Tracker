import os
import time
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Track seen tokens
seen_tokens = set()
AGE_FILTER = 24  # default = 24H

# -------------------------------
# Telegram Bot Handlers
# -------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("24H", callback_data="age_24"),
            InlineKeyboardButton("3DAYS", callback_data="age_72"),
            InlineKeyboardButton("7DAYS", callback_data="age_168"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🤖 Welcome! Choose how old tokens you want to track:", reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global AGE_FILTER
    query = update.callback_query
    await query.answer()

    if query.data == "age_24":
        AGE_FILTER = 24
        msg = "✅ Now tracking tokens ≤ 24 hours old."
    elif query.data == "age_72":
        AGE_FILTER = 72
        msg = "✅ Now tracking tokens ≤ 3 days old."
    elif query.data == "age_168":
        AGE_FILTER = 168
        msg = "✅ Now tracking tokens ≤ 7 days old."
    else:
        msg = "⚠️ Unknown option."

    await query.edit_message_text(text=msg)

# -------------------------------
# DexScreener Token Fetch
# -------------------------------

def fetch_tokens():
    url = "https://api.dexscreener.com/latest/dex/search?q=solana"
    response = requests.get(url)
    if response.status_code != 200:
        print("❌ API error:", response.text)
        return []
    return response.json().get("pairs", [])

async def check_new_tokens(context: ContextTypes.DEFAULT_TYPE):
    global seen_tokens, AGE_FILTER
    pairs = fetch_tokens()
    if not pairs:
        return

    now = time.time()

    for pair in pairs:
        token_address = pair["baseToken"]["address"]
        created_at = pair.get("info", {}).get("createdAt", None)

        # Skip if already seen
        if token_address in seen_tokens:
            continue

        # Apply age filter (if API gives createdAt timestamp)
        if created_at:
            token_age_hours = (now - (created_at / 1000)) / 3600
            if token_age_hours > AGE_FILTER:
                continue

        seen_tokens.add(token_address)

        # Detect chain
        chain = pair.get("chainId", "Unknown").capitalize()

        name = pair["baseToken"]["name"]
        symbol = pair["baseToken"]["symbol"]
        url = pair["url"]

        message = (
            f"🚀 <b>New {chain} Token Detected!</b>\n\n"
            f"<b>Name:</b> {name}\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Chart:</b> {url}"
        )

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
    app.add_handler(CallbackQueryHandler(button))

    # Background job to check tokens every 60s
    app.job_queue.run_repeating(check_new_tokens, interval=60, first=5)

    print("🤖 Bot started! Now watching for new tokens...")
    app.run_polling()

if __name__ == "__main__":
    main()
