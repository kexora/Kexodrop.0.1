import os
import yt_dlp
import requests
import asyncio
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
MAX_FILE_SIZE_MB = 100

async def is_under_100mb(url: str) -> bool:
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        size_bytes = int(response.headers.get('Content-Length', 0))
        return size_bytes < (MAX_FILE_SIZE_MB * 1024 * 1024)
    except Exception as e:
        print(f"Size check failed: {e}")
        return True  # Proceed if unable to check

def download_video(url: str) -> str:
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'mp4/best',
        'merge_output_format': 'mp4',
        'quiet': True,
        'cookies': 'cookies.txt',  # For private video support
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if not filename.endswith('.mp4'):
            filename = filename.rsplit('.', 1)[0] + '.mp4'
        return filename

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip().lower()

    if any(greet in user_text for greet in ["hello", "hi", "jai", "jai ho"]):
        await update.message.reply_text("Welcome to Kexodrop!")
        return

    if user_text.startswith("http"):
        msgs_to_delete = []

        msg1 = await update.message.reply_text("Checking link...")
        msgs_to_delete.append(msg1.message_id)

        if not await is_under_100mb(user_text):
            await update.message.reply_text(f"File is larger than {MAX_FILE_SIZE_MB}MB.")
            return

        msg2 = await update.message.reply_text("Searching...")
        msgs_to_delete.append(msg2.message_id)

        msg3 = await update.message.reply_text("Wait...")
        msgs_to_delete.append(msg3.message_id)

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

        try:
            video_path = await asyncio.to_thread(download_video, user_text)

            # Delete temporary bot messages
            for msg_id in msgs_to_delete:
                try:
                    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id)
                except:
                    pass

            with open(video_path, 'rb') as video_file:
                await update.message.reply_video(video=video_file)

            os.remove(video_path)

        except Exception as e:
            print("Download error:", e)
            await update.message.reply_text("Sorry, video couldn't be downloaded. It might be private or blocked.")
    else:
        await update.message.reply_text("Send a valid video link or say hello!")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
