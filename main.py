import os, json, time, random, qrcode, yt_dlp
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_TOKEN") or "8773409457:AAG9VvGq0mgsJ0hpiGrIm_zoSRXglhLn4_M" # Render pe env me daal dena better hai
ADMIN_ID = 7166502503
VAULT_ID = -1004353152847
UPI_ID = "s.maddheshia@ptaxis"
DB_FILE = "database.json"

PLANS = {
    "1day": {"price": 10, "days": 1, "label": "1 Day - ₹10"},
    "1week": {"price": 30, "days": 7, "label": "1 Week - ₹30"},
    "1month": {"price": 69, "days": 30, "label": "1 Month - ₹69"},
    "2month": {"price": 150, "days": 60, "label": "2 Months - ₹150"}
}

def load_db():
    if not os.path.exists(DB_FILE): return {}
    try:
        with open(DB_FILE, 'r') as f: return json.load(f)
    except: return {}

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=2)

def get_user(uid):
    db = load_db()
    uid = str(uid)
    if uid not in db:
        db[uid] = {"free_used": 0, "premium_until": 0, "videos": []}
        save_db(db)
        return db[uid]
    return db[uid]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    user = get_user(uid)
    is_prem = user['premium_until'] > time.time()
    free_left = 2 - user['free_used']

    if is_prem:
        exp = datetime.fromtimestamp(user['premium_until']).strftime("%d-%m-%Y")
        plan_text = f"🔥 PREMIUM Active till {exp}"
    else:
        plan_text = f"Free Member ({max(0,free_left)}/2 left)"

    text = f"""
👋 *Welcome {update.effective_user.first_name}!*

⚡️ *OneClick Vault Pro - Fastest Downloader*

👤 Name: {update.effective_user.first_name}
💎 Plan: {plan_text}
🗃️ Vault: {len(user['videos'])} videos

*Just send any Insta / FB / YT link, I'll download it!*
"""
    kb = [
        [InlineKeyboardButton("🚀 Unlock Premium", callback_data="go_premium")],
        [InlineKeyboardButton("🗃️ My Vault", callback_data="my_vault"), InlineKeyboardButton("👤 My Profile", callback_data="my_profile")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = q.data
    user = get_user(uid)

    if data == "go_premium":
        kb = [[InlineKeyboardButton(v['label'], callback_data=f"buy_{k}")] for k,v in PLANS.items()]
        kb.append([InlineKeyboardButton("⬅️ Back to Home", callback_data="back_home")])
        await q.edit_message_text("💎 *Unlock Premium - Unlimited Downloads*\n\nSelect Plan 👇\nUPI: `s.maddheshia@ptaxis`", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    elif data.startswith("buy_"):
        key = data.split("_")[1]
        plan = PLANS[key]
        order_id = f"OC{random.randint(10000,99999)}"
        upi_link = f"upi://pay?pa={UPI_ID}&pn=OneClick&am={plan['price']}&cu=INR&tn={order_id}"
        img = qrcode.make(upi_link)
        img.save(f"{order_id}.png")

        caption = f"""
🧾 *Payment Invoice*

📦 Plan: {plan['label']}
💰 Amount: *₹{plan['price']}*
🆔 Order ID: `{order_id}`
⏳ Valid: 2 Minutes
💳 UPI: `{UPI_ID}`

⚠️ *Exact amount pay karo, warna approve nahi hoga.*
Pay karke *I Have Paid* dabao.
"""
        kb = [[InlineKeyboardButton("✅ I Have Paid", callback_data=f"paid_{order_id}_{key}")],[InlineKeyboardButton("❌ Cancel", callback_data="go_premium")]]
        try:
            await context.bot.send_photo(chat_id=q.from_user.id, photo=open(f"{order_id}.png",'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
            os.remove(f"{order_id}.png")
        except:
            await q.edit_message_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    elif data.startswith("paid_"):
        _, order_id, key = data.split("_")
        plan = PLANS[key]
        admin_msg = f"💰 *New Payment Alert!*\n\n👤 User: {q.from_user.first_name} (`{uid}`)\n📦 Plan: {plan['label']}\n💰 Amount: ₹{plan['price']}\n🆔 Order: `{order_id}`\n\nApprove: `/approve {uid} {plan['days']}`"
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode="Markdown")
        await context.bot.send_message(chat_id=q.from_user.id, text="✅ *Payment Request Sent!*\n\nAdmin 2-3 min me approve kar dega. Thoda wait karo bhai.", parse_mode="Markdown")

    elif data == "my_profile":
        is_prem = user['premium_until'] > time.time()
        exp = datetime.fromtimestamp(user['premium_until']).strftime("%d-%m-%Y %H:%M") if is_prem else "Not Active"
        txt = f"👤 *My Profile*\n\n🆔 ID: `{uid}`\n💎 Status: {'🔥 PREMIUM till '+exp if is_prem else 'Free (2/2 limit)'}\n🎬 Used: {user['free_used']}/2\n🗃️ Saved: {len(user['videos'])}"
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_home")]]), parse_mode="Markdown")

    elif data == "my_vault":
        if not user['videos']:
            await q.edit_message_text("🗃️ *Vault Empty!*\nKoi video save nahi hai abhi.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_home")]]), parse_mode="Markdown")
        else:
            last = "\n".join([f"{i+1}. {v[:50]}" for i,v in enumerate(user['videos'][-5:])])
            await q.edit_message_text(f"🗃️ *My Vault - {len(user['videos'])} Videos*\n\nLast 5:\n{last}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_home")]]), parse_mode="Markdown")

    elif data == "back_home":
        # re-send home
        is_prem = user['premium_until'] > time.time()
        exp = datetime.fromtimestamp(user['premium_until']).strftime("%d-%m-%Y") if is_prem else "Free"
        text = f"👋 *Welcome {q.from_user.first_name}!*\n\n💎 Plan: {exp}\nJust send any link!"
        kb = [[InlineKeyboardButton("🚀 Unlock Premium", callback_data="go_premium")],[InlineKeyboardButton("🗃️ My Vault", callback_data="my_vault"), InlineKeyboardButton("👤 My Profile", callback_data="my_profile")]]
        try:
            await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except: pass

async def approve_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID: return
    try:
        tid = str(context.args[0]); days = int(context.args[1])
        db = load_db()
        if tid not in db: db[tid] = {"free_used":0,"premium_until":0,"videos":[]}
        db[tid]['premium_until'] = time.time() + days*86400
        save_db(db)
        await update.message.reply_text(f"✅ Approved {tid} for {days} days")
        await context.bot.send_message(chat_id=int(tid), text=f"🎉 *Premium Activated!*\n{days} days ke liye active ho gaya! Ab unlimited download karo 🔥", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Use: /approve user_id days\nError: {e}")

async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    db = load_db()
    if uid not in db: db[uid] = {"free_used":0,"premium_until":0,"videos":[]}
    user = db[uid]
    is_prem = user['premium_until'] > time.time()

    if not is_prem and user['free_used'] >= 2:
        kb = [[InlineKeyboardButton("🚀 Buy Premium ₹10", callback_data="go_premium")]]
        await update.message.reply_text("❌ *Free Limit Over! 2/2 Used*\n\nPremium lo unlimited ke liye 👇", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        return

    url = update.message.text.strip()
    if "http" not in url: return
    msg = await update.message.reply_text("⏳ *Downloading... Please wait 5 sec*", parse_mode="Markdown")

    # YOUTUBE FIX - 100% WORKING CONFIG
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': '%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
            }
        },
        'http_headers': {
            'User-Agent': 'com.google.android.youtube/17.36.4 (Linux; U; Android 12; SM-G991B) gzip'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Save to Vault
        sent = await context.bot.send_video(chat_id=VAULT_ID, video=open(filename,'rb'), caption=f"User:{uid}\n{url}")
        await context.bot.send_video(chat_id=update.effective_user.id, video=sent.video.file_id, caption="✅ *Here is your video! Saved in Vault 🗃️*", parse_mode="Markdown")

        db = load_db()
        db[uid]['videos'].append(url)
        if not is_prem: db[uid]['free_used'] += 1
        save_db(db)
        await msg.delete()
        if os.path.exists(filename): os.remove(filename)

    except Exception as e:
        print(f"Error: {e}")
        await msg.edit_text(f"❌ *Download Fail:* {str(e)[:300]}\n\nTry another link or update bot.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("approve", approve_cmd))
    app.add_handler(CallbackQueryHandler(cb_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_handler))
    print("Bot Started with YouTube Fix...")
    app.run_polling()

if __name__ == "__main__":
    main()