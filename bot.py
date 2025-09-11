import os
import time
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime, timezone

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Global vars
AGE_FILTER = None   # in hours
CHAIN = None        # solana / ethereum / etc
seen_tokens = set() # track already alerted

# ---- START ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Solana", callback_data="chain_solana"),
            InlineKeyboardButton("Ethereum", callback_data="chain_ethereum"),
        ]
    ]
    await update.message.reply_text("👋 Select blockchain:", reply_markup=InlineKeyboardMarkup(keyboard))

# ---- BUTTON ----
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAIN, AGE_FILTER
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("chain_"):
        CHAIN = data.split("_")[1]
        keyboard = [
            [
                InlineKeyboardButton("24H", callback_data="age_24"),
                InlineKeyboardButton("72H", callback_data="age_72"),
                InlineKeyboardButton("168H", callback_data="age_168"),
            ]
        ]
        await query.edit_message_text(f"✅ Selected chain: {CHAIN}\nNow choose max token age:", 
                                      reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("age_"):
        AGE_FILTER = int(data.split("_")[1])
        await query.edit_message_text(f"✅ Selected chain: {CHAIN}\n✅ Selected age filter: {AGE_FILTER} hours\n\n🤖 Bot is now tracking tokens...")

# ---- FETCH TOKENS ----
def fetch_tokens():
    if not CHAIN:
        return []

    url = f"https://api.dexscreener.com/latest/dex/pairs/{CHAIN}"
    response = requests.get(url)
    if response.status_code != 200:
        print("❌ API error:", response.text)
        return []

    return response.json().get("pairs", [])


# ---- CHECK NEW TOKENS ----
def check_new_tokens(context: ContextTypes.DEFAULT_TYPE):
    if not CHAIN or not AGE_FILTER:
        return

    pairs = fetch_tokens()
    if not pairs:
        return

    now = datetime.now(timezone.utc)

    for pair in pairs:
        token_address = pair["baseToken"]["address"]
        created_at = pair.get("pairCreatedAt")  # in ms

        if not created_at:
            continue

        created_dt = datetime.fromtimestamp(created_at / 1000, tz=timezone.utc)
        age_hours = (now - created_dt).total_seconds() / 3600

        # ✅ filter by user selection
        if age_hours > AGE_FILTER:
            continue

        if token_address in seen_tokens:
            continue
        seen_tokens.add(token_address)

        # prepare message
        name = pair["baseToken"]["name"]
        symbol = pair["baseToken"]["symbol"]
        url = pair["url"]
        chain = pair["chainId"].capitalize()

        message = (
            f"🚀 <b>New {chain} Pair Detected!</b>\n\n"
            f"<b>Name:</b> {name}\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Age:</b> {age_hours:.2f} hours\n"
            f"<b>Chart:</b> {url}"
        )

        context.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="HTML")
        print("✅ Alert sent:", name, symbol, f"({age_hours:.1f}h old)")

# ---- MAIN ----
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    app.job_queue.run_repeating(check_new_tokens, interval=60, first=10)

    print("🤖 Bot started! Waiting for /start ...")
    app.run_polling()

if __name__ == "__main__":
    main()
