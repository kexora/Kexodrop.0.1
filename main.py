import os
import requests
import yt_dlp
from telegram import ChatAction
from telegram.ext import Updater, MessageHandler, Filters

# Telegram Bot Token from environment variable or hardcoded fallback
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

MAX_FILE_SIZE_MB = 100

def is_under_100mb(url):
    try:
        response = requests.head(url, allow_redirects=True)
        size_bytes = int(response.headers.get('Content-Length', 0))
        return size_bytes < (MAX_FILE_SIZE_MB * 1024 * 1024)
    except Exception as e:
        print("Size check failed:", e)
        return True  # In case of error, allow it (yt-dlp will catch download size)

def download_video(url):
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'merge_output_format': 'mp4',
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if not filename.endswith('.mp4'):
            filename = filename.rsplit('.', 1)[0] + '.mp4'
        return filename

def handle_message(update, context):
    user_text = update.message.text.lower()

    # 1. Welcome message
    if user_text in ["hi", "hello", "hey"]:
        update.message.reply_text("Welcome to Kexodrop!")
        return

    # 2. Handle link
    if user_text.startswith("http"):
        if is_under_100mb(user_text):
            update.message.reply_text("Searching...")
            update.message.reply_text("Wait...")
            context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

            try:
                video_path = download_video(user_text)
                context.bot.send_video(chat_id=update.effective_chat.id, video=open(video_path, 'rb'))
                os.remove(video_path)  # Clean up
            except Exception as e:
                update.message.reply_text("Failed to download or send the video.")
                print("Download/Send error:", e)
        else:
            update.message.reply_text("Sorry, the file size is over 100MB.")
    else:
        update.message.reply_text("Please send a valid video link.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
