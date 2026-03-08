import os
import re
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, CommandHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

url_regex = re.compile(r'https?://')

# لتخزين حالة المستخدم عند /vtom
vtom_users = set()

async def start_vtom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    vtom_users.add(user_id)
    await update.message.reply_text(
        "ارسل الفيديو لتحويله الى بصمة (المقطع الصوتي)\n\nصانع البوت ----» @wi6j1"
    )

async def handle_video_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in vtom_users:
        vtom_users.remove(user_id)
        # حفظ الفيديو مؤقتًا
        video_file = await update.message.video.get_file()
        file_path = f"{user_id}_video.mp4"
        await video_file.download_to_drive(file_path)

        # تحويل الفيديو إلى صوت باستخدام yt-dlp (FFmpeg)
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{user_id}_audio.%(ext)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }],
            "quiet": True
        }

        # yt-dlp يتطلب رابط، لذا نستخدم ffmpeg مباشرة
        import subprocess
        audio_path = f"{user_id}_audio.mp3"
        cmd = ["ffmpeg", "-y", "-i", file_path, "-vn", "-ab", "192k", audio_path]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        await update.message.reply_audio(
            audio=open(audio_path, "rb"),
            caption="تم تحويل الفيديو الى بصمة (MP3)\nصانع البوت ----» @wi6j1"
        )

        # حذف الملفات المؤقتة
        os.remove(file_path)
        os.remove(audio_path)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    # تحقق إذا المستخدم في حالة /vtom
    user_id = update.message.from_user.id
    if user_id in vtom_users:
        await update.message.reply_text(
            "ارسل الفيديو لتحويله الى بصمة (المقطع الصوتي)\n\nصانع البوت ----» @wi6j1"
        )
        return

    if not url_regex.search(text):
        await update.message.reply_text(
            "حبيبي حط رابط تضحك عليه انته ههههههههههههههههههههههههههههههههه\n\n"
            "صانع البوت ----» @wi6j1"
        )
        return

    context.user_data["url"] = text

    buttons = [
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

        if query.data == "video":

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

# أوامر
app.add_handler(CommandHandler("vtom", start_vtom))

# رسالة الفيديو للمقطع الصوتي
app.add_handler(MessageHandler(filters.VIDEO, handle_video_message))

# باقي الرسائل
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

# أزرار
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()
