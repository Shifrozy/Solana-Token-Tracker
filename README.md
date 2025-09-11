# 🚀 Solana & Ethereum New Token Tracker Telegram Bot

A **Telegram bot** that automatically tracks **new tokens** listed on [DexScreener](https://dexscreener.com/) for Solana, Ethereum, and other supported chains.  
The bot notifies you directly in Telegram with token details such as **name, symbol, chain, age, and DexScreener chart link**.  

---

## ✨ Features

- 🔍 Detects **brand-new token pairs** on Solana, Ethereum, etc.  
- 🕒 User-selectable **token age filter** (24h, 72h, or 168h).  
- ⚡ **Real-time updates** — checks every 30–60 seconds.  
- 📲 Sends clean Telegram alerts with:
  - Token Name & Symbol  
  - Blockchain (Solana, Ethereum, etc.)  
  - Token Age (hours since launch)  
  - Direct DexScreener Chart Link  
- 🚫 Prevents duplicate alerts for the same token.  

---

## 📦 Requirements

- Python **3.10+**
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)  
- Your Telegram **chat ID**  

Install dependencies:
```bash
pip install python-telegram-bot==20.6 requests python-dotenv
```

### ⚙️ Setup

Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/solana-token-tracker.git
cd solana-token-tracker
```

## Create a .env file in the project root:
```env
BOT_TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id
```

## Run the bot:
```bash
python bot.py
```
## 🚀 Usage
1.Start the bot in Telegram with /start.

2.Select the blockchain (Solana or Ethereum).

3.Choose how old tokens can be:

4.24H → Tokens created in the last 24 hours

5.72H → Tokens created in the last 3 days

6.168H → Tokens created in the last 7 days

Receive instant token alerts directly in Telegram.

## 📸 Example Alert
```makefile
🚀 New Solana Pair Detected!

Name: ExampleToken
Symbol: EXT
Age: 5.3 hours
Chart: https://dexscreener.com/solana/xxxxxxxx
```
## 🛠 Customization

Change scan interval in bot.py:
```bash
app.job_queue.run_repeating(check_new_tokens, interval=30, first=10)
```
##🔒 Disclaimer
```bash
This bot fetches live data from DexScreener.
It is intended for educational and informational purposes only.
Do your own research before trading or investing in any token.
```
## 🤝 Contributing
```bash
Pull requests and suggestions are welcome!
If you find an issue, please open an issue
 on GitHub.
 ```



