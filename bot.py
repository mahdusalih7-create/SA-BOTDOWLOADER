import os
import re
import glob
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

url_regex = re.compile(r'https?://')

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if not url_regex.search(text):
        await update.message.reply_text(
            "حبيبي حط رابط تضحك عليه انته ههههههههههههههههههههههههههههههههه\n\n"
            "صانع البوت ----» @wi6j1"
        )
        return

    context.user_data["url"] = text

    buttons = [
        [InlineKeyboardButton("📷 تحميل كصورة", callback_data="image")],
        [InlineKeyboardButton("🎧 تحميل كملف صوتي", callback_data="voice")],
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

    try:

        if query.data == "image":
            ydl_opts = {
                "skip_download": True,
                "write_all_thumbnails": True,
                "outtmpl": "img.%(ext)s",
                "quiet": True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)

            images = glob.glob("*.jpg") + glob.glob("*.png") + glob.glob("*.webp")

            for img in images:
                await query.message.reply_photo(
                    photo=open(img, "rb"),
                    caption="صانع البوت ----» @wi6j1"
                )
                os.remove(img)

        elif query.data == "video":
            ydl_opts = {
                "format": "best",
                "outtmpl": "video.%(ext)s",
                "quiet": True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

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

            await query.message.reply_voice(
                voice=open(filename, "rb"),
                caption="صانع البوت ----» @wi6j1"
            )

            os.remove(filename)

    except:
        await query.message.reply_text(
            "غلط بالرابط تاكد منه\n\nصانع البوت ----» @wi6j1"
        )


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()
