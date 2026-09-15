import os, requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "https://oneclick-backend-6g5a.onrender.com")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Link bhejo - 1800+ Sites Supported 🔥")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"): return
    msg = await update.message.reply_text("⏳ Backend se fetch kar raha hu...")
    try:
        r = requests.post(f"{BACKEND_URL}/api/download", json={"url": url, "device_id": str(update.effective_user.id)}, timeout=120)
        data = r.json()
        if data.get("download_url"):
            await update.message.reply_video(video=data["download_url"], caption=f"{data.get('title','Your Video')} ✅")
            await msg.delete()
        else:
            await msg.edit_text(f"❌ Fail: {data.get('error')}")
    except Exception as e:
        await msg.edit_text(f"❌ Error: {e}")

async def post_init(application):
    await application.bot.delete_webhook(drop_pending_updates=True)
    print("Webhook deleted, polling started")

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.run_polling()

if __name__ == "__main__":
    main()
