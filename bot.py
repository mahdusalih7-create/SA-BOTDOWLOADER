import os
import re
import yt_dlp
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters, CommandHandler, ConversationHandler

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 5057151278  # ايدي المالك
MESSAGE = 0

url_regex = re.compile(r'https?://')

def fix_tiktok_url(url):
    try:
        r = requests.get(url, allow_redirects=True)
        url = r.url
    except:
        pass
    if "/photo/" in url:
        url = url.replace("/photo/", "/video/")
    return url

# حفظ كل مستخدم يتفاعل مع البوت
def save_user(user_id):
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        users = []
    if user_id not in users:
        users.append(user_id)
        with open("users.json", "w") as f:
            json.dump(users, f)

# التعامل مع الرسائل العادية
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)

    text = update.message.text

    # امر البث للمالك
    if update.effective_user.id == OWNER_ID and text == "/allm":
        await update.message.reply_text("ارسل الرسالة التي تريد ارسالها لجميع المستخدمين:")
        return MESSAGE

    if not url_regex.search(text):
        await update.message.reply_text(
            "حبيبي حط رابط تضحك عليه انته ههههههههههههههههههههههههههههههههه\n\n"
            "صانع البوت ----» @wi6j1"
        )
        return

    url = fix_tiktok_url(text)
    context.user_data["url"] = url

    buttons = [
        [InlineKeyboardButton("📷 تحميل كصورة", callback_data="image")],
        [InlineKeyboardButton("🎧 تحميل كبصمة", callback_data="voice")],
        [InlineKeyboardButton("🎥 تحميل كفيديو", callback_data="video")]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "اختر نوع التحميل\n\nصانع البوت ----» @wi6j1",
        reply_markup=keyboard
    )

# التعامل مع الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    if not url:
        await query.edit_message_text("غلط بالرابط تأكد منه\n\nصانع البوت ----» @wi6j1")
        return

    rocket = await query.message.reply_text("🚀")

    try:
        if query.data == "image":
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(url, download=False)
            first_image = info["thumbnails"][0]["url"] if info.get("thumbnails") else None
            if first_image:
                await query.message.reply_text("✅")
                await query.message.reply_photo(photo=first_image, caption="صانع البوت ----» @wi6j1")

        elif query.data == "video":
            ydl_opts = {"format": "best", "outtmpl": "video.%(ext)s", "quiet": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            await query.message.reply_text("✅")
            await query.message.reply_video(video=open(filename, "rb"), caption="صانع البوت ----» @wi6j1")
            os.remove(filename)

        elif query.data == "voice":
            ydl_opts = {"format": "bestaudio/best", "outtmpl": "voice.%(ext)s", "quiet": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            await query.message.reply_text("✅")
            await query.message.reply_voice(voice=open(filename, "rb"), caption="صانع البوت ----» @wi6j1")
            os.remove(filename)

        await rocket.delete()

    except:
        await rocket.delete()
        await query.message.reply_text("غلط بالرابط تاكد منه\n\nصانع البوت ----» @wi6j1")

# مرحلة استقبال نص البث
async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return ConversationHandler.END

    message = update.message.text
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        users = []

    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
        except:
            pass

    await update.message.reply_text("تم ارسال الرسالة لجميع المستخدمين ✅")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم الغاء العملية ✅")
    return ConversationHandler.END

app = ApplicationBuilder().token(TOKEN).build()

broadcast_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.TEXT & filters.Regex(r'^/allm$'), broadcast_message)],
    states={MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_message)]},
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(broadcast_handler)

app.run_polling()
