import os
import os
os.system("pip install -U yt-dlp") # Ye YouTube wala error fix karega
import telebot
import os
os.system("pip install -U yt-dlp") # Ye YouTube wala error fix karega
from flask import Flask
from telebot import types
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "OneClick Bot LIVE ✅"
def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
Thread(target=run).start()

BOT_TOKEN = "8773409457:AAH7kSoJdeuDHwfZclKp1FhOY4e-kVZ6guo"  # Token yahan daalo
bot = telebot.TeleBot(BOT_TOKEN)

# --- Menu Function ---
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

# --- Button Dabane pe kya hoga ---
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.answer_callback_query(call.id) # Button ka loading hatayega
    
    if call.data == "insta":
        bot.send_message(call.message.chat.id, "📸 Instagram Link bhejo Boss, mai download karke deta hu!")
    elif call.data == "yt":
        bot.send_message(call.message.chat.id, "▶️ YouTube Link bhejo Boss!")
    elif call.data == "fb":
        bot.send_message(call.message.chat.id, "👍 Facebook Link bhejo Boss!")

# --- Link aane pe ---
@bot.message_handler(func=lambda m: "http" in m.text)
def link_handler(m):
    bot.reply_to(m, f"⏳ Link mil gaya: {m.text}\nDownloading start kar raha hu...")
    # Yahan tumhara download wala code aayega

print("Bot Started with Buttons")
bot.infinity_polling()
