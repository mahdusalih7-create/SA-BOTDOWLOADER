import os
import re
import yt_dlp
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

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

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

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

            first_image = None

            if "thumbnails" in info and info["thumbnails"]:
                first_image = info["thumbnails"][0]["url"]

            if first_image:
                await query.message.reply_text("✅")
                await query.message.reply_photo(
                    photo=first_image,
                    caption="صانع البوت ----» @wi6j1"
                )

        elif query.data == "video":

            ydl_opts = {
                "format": "best",
                "outtmpl": "video.%(ext)s",
                "quiet": True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            await query.message.reply_text("✅")
            await query.message.reply_video(
                video=open(filename, "rb"),
                caption="صانع البوت ----» @wi6j1"
            )

            os.remove(filename)

        elif query.data == "voice":

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "voice.%(ext)s",
                "quiet": True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            await query.message.reply_text("✅")
            await query.message.reply_voice(
                voice=open(filename, "rb"),
                caption="صانع البوت ----» @wi6j1"
            )

            os.remove(filename)

        await rocket.delete()

    except:
        await rocket.delete()
        await query.message.reply_text(
            "غلط بالرابط تاكد منه\n\nصانع البوت ----» @wi6j1"
        )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()
