import os
import requests
from telegram.ext import Updater, MessageHandler, Filters
from telegram import ChatAction

# Replace with your actual token or set via environment variable
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

MAX_FILE_SIZE_MB = 100

def is_under_100mb(url):
    try:
        response = requests.head(url, allow_redirects=True)
        size_bytes = int(response.headers.get('Content-Length', 0))
        return size_bytes < (MAX_FILE_SIZE_MB * 1024 * 1024)
    except Exception as e:
        print("Size check failed:", e)
        return False

def download_video(url):
    # Dummy function — replace this with actual yt_dlp or similar download logic
    file_path = "video.mp4"
    # Example download code (placeholder)
    with open(file_path, 'wb') as f:
        f.write(b'dummy video content')
    return file_path

def handle_message(update, context):
    user_text = update.message.text.lower()

    # 1. Welcome response
    if user_text in ["hi", "hello", "hey"]:
        update.message.reply_text("Welcome to Kexodrop!")
        return

    # 2. Check if it's a video link
    if user_text.startswith("http"):
        if is_under_100mb(user_text):
            update.message.reply_text("Searching...")
            update.message.reply_text("Wait...")
            context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

            video_path = download_video(user_text)
            try:
                context.bot.send_video(chat_id=update.effective_chat.id, video=open(video_path, 'rb'))
            except Exception as e:
                update.message.reply_text("Failed to send video.")
                print("Send error:", e)
            finally:
                if os.path.exists(video_path):
                    os.remove(video_path)
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
