import os
import logging
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Logging
logging.basicConfig(level=logging.INFO)

# Ensure downloads folder exists
os.makedirs("downloads", exist_ok=True)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

ad_text = ""

async def set_ad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ad_text
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Aap admin nahi hain.")
        return
    ad_text = " ".join(context.args)
    await update.message.reply_text(f"Ad text set kiya gaya: {ad_text}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    searching_msg = await update.message.reply_text("Searching...")
    wait_msg = await update.message.reply_text("Please wait...")

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > 500:
            await update.message.reply_text("Error: File size 500MB se zyada hai.")
            os.remove(file_path)
            await searching_msg.delete()
            await wait_msg.delete()
            return

        title = info.get('title', 'File')
        if ad_text:
            title += " | " + ad_text

        await context.bot.send_document(chat_id=update.effective_chat.id, document=open(file_path, 'rb'), filename=title)
        os.remove(file_path)
        await searching_msg.delete()
        await wait_msg.delete()

    except Exception as e:
        await update.message.reply_text(f"Download error: {e}")
        await searching_msg.delete()
        await wait_msg.delete()

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("setad", set_ad))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()