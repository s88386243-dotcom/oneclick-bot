import os
os.system("pip install -U yt-dlp")

import telebot
from flask import Flask
from telebot import types
from threading import Thread
import yt_dlp

app = Flask('')
@app.route('/')
def home(): return "OneClick Bot LIVE ✅"
def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
Thread(target=run).start()

BOT_TOKEN = "8773409457:AAG9VvGq0mgsJ0hpiGrIm_zoSRXglhLn4_M"
bot = telebot.TeleBot(BOT_TOKEN)

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Instagram 📸", callback_data="insta"),
        types.InlineKeyboardButton("YouTube ▶️", callback_data="yt"),
        types.InlineKeyboardButton("Facebook 👍", callback_data="fb")
    )
    return markup

@bot.message_handler(commands=['start', 'help', 'download'])
def start(m):
    bot.send_message(m.chat.id, "Hi Boss! 👋 Category select karo:", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.answer_callback_query(call.id)
    if call.data == "insta":
        bot.send_message(call.message.chat.id, "📸 Instagram Link bhejo Boss!")
    elif call.data == "yt":
        bot.send_message(call.message.chat.id, "▶️ YouTube Link bhejo Boss!")
    elif call.data == "fb":
        bot.send_message(call.message.chat.id, "👍 Facebook Link bhejo Boss!")

@bot.message_handler(func=lambda m: "http" in m.text)
def download_video(m):
    url = m.text
    bot.reply_to(m, f"⏳ Link mil gaya Boss... Downloading start kar raha hu...")
    
    try:
        # YouTube error fix ke liye ye options
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
        with open(filename, 'rb') as video:
            bot.send_video(m.chat.id, video, caption=f"✅ Ho gaya download Boss!\n{info.get('title')}")
        
        os.remove(filename) # File delete karke jagah khali
        
    except Exception as e:
        bot.send_message(m.chat.id, f"Failed: {e}\nEk baar dusra link try karo.")

print("Bot Started FINAL")
bot.infinity_polling()
