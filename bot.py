import os
from flask import Flask
import threading

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask).start()
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

# --- YAHAN APNA SETUP KARO BOSS ---
BOT_TOKEN = "8773409457:AAH7kSoJdeuDHwfZclKp1FhOY4e-kVZ6guo"
CHANNEL_USERNAME = "@ApnaChannelUsername" # @ hata ke apna channel ka username daalo, jaise @oneclick_earning
CHANNEL_LINK = "https://t.me/ApnaChannelUsername"
# ---------------------------------

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            keyboard = [[InlineKeyboardButton("📢 Channel Join Karo", url=CHANNEL_LINK)]]
            await update.message.reply_text(
                f"Boss video se pehle channel join karna padega 🙏\n\nJoin karke /start dobara dabao.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return False
    except:
        return True # Agar bot admin nahi hai to check skip

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update, context): return
    keyboard = [[InlineKeyboardButton("Instagram 📸", callback_data='insta'), InlineKeyboardButton("YouTube ▶️", callback_data='yt')], [InlineKeyboardButton("Facebook 👍", callback_data='fb')]]
    await update.message.reply_text("Hi Boss! 👋 Category select karo:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['category'] = query.data
    await query.edit_message_text("Link bhejo Boss, ab aapko 3 option milenge: Video, MP3, Thumbnail 🔥")

async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update, context): return
    url = update.message.text.strip()
    if not url.startswith("http"): return

    context.user_data['url'] = url
    keyboard = [[InlineKeyboardButton("🎬 Video (MP4)", callback_data='get_video'), InlineKeyboardButton("🎵 Audio (MP3)", callback_data='get_audio')], [InlineKeyboardButton("🖼️ Thumbnail", callback_data='get_thumb')]]
    await update.message.reply_text("Kya download karna hai Boss?", reply_markup=InlineKeyboardMarkup(keyboard))

async def process_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    url = context.user_data.get('url')
    choice = query.data
    await query.edit_message_text("⏳ Downloading... 30 sec ruko Boss...")

    ydl_opts_video = {'outtmpl': '%(title)s.%(ext)s', 'format': 'best[ext=mp4]/best', 'socket_timeout': 60, 'retries': 10}
    ydl_opts_audio = {'outtmpl': '%(title)s.%(ext)s', 'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192',}], 'socket_timeout': 60}

    try:
        if choice == 'get_thumb':
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                thumb_url = info.get('thumbnail')
            await context.bot.send_photo(chat_id=query.message.chat_id, photo=thumb_url, caption="Lo Boss Thumbnail 🖼️")
            return

        opts = ydl_opts_audio if choice == 'get_audio' else ydl_opts_video
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if choice == 'get_audio': filename = os.path.splitext(filename)[0] + ".mp3"

        if choice == 'get_audio':
            await context.bot.send_audio(audio=open(filename, 'rb'), chat_id=query.message.chat_id, caption="Lo Boss MP3 🎵")
        else:
            await context.bot.send_video(video=open(filename, 'rb'), chat_id=query.message.chat_id, caption="Lo Boss Video ✅")
        os.remove(filename)
    except Exception as e:
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"Failed: {e}")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_click, pattern="^(insta|yt|fb)$"))
app.add_handler(CallbackQueryHandler(process_download, pattern="^get_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_handler))
print("Pro Bot Started... ✅")
app.run_polling()
