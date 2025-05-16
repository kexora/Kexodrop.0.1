import os
import requests
import yt_dlp
from telegram import ChatAction
from telegram.ext import Updater, MessageHandler, Filters

# Telegram Bot Token
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

MAX_FILE_SIZE_MB = 100

# Size check (HEAD request)
def is_under_100mb(url):
    try:
        response = requests.head(url, allow_redirects=True)
        size_bytes = int(response.headers.get('Content-Length', 0))
        return size_bytes < (MAX_FILE_SIZE_MB * 1024 * 1024)
    except Exception as e:
        print("Size check failed, allowing:", e)
        return True  # fallback if HEAD fails

# yt-dlp based download with cookies
def download_video(url):
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'merge_output_format': 'mp4',
        'quiet': True,
        'cookies': 'cookies.txt'  # make sure this file exists
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if not filename.endswith('.mp4'):
            filename = filename.rsplit('.', 1)[0] + '.mp4'
        return filename

# Main handler
def handle_message(update, context):
    user_text = update.message.text.lower()

    # Greeting
    if any(word in user_text for word in ["hello", "hi", "jai", "jai ho"]):
        update.message.reply_text("Welcome to Kexodrop!")
        return

    # If it's a link
    if user_text.startswith("http"):
        update.message.reply_text("Checking link...")

        if is_under_100mb(user_text):
            update.message.reply_text("Searching...")
            update.message.reply_text("Wait...")
            context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

            try:
                video_path = download_video(user_text)
                context.bot.send_video(chat_id=update.effective_chat.id, video=open(video_path, 'rb'))
                os.remove(video_path)
            except Exception as e:
                print("Error during download/send:", e)
                update.message.reply_text("Sorry, video couldn't be downloaded. It might be private or blocked.")
        else:
            update.message.reply_text("File is too large (over 100MB).")
    else:
        update.message.reply_text("Send a valid video link or say hello!")

# Entry point
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
