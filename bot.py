import os
import logging
from pyrogram import Client
from plugins.config import Config

# Configure logging to see errors in the console
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":

    # 🚨 SECURITY WARNING SECTION 🚨
    print("\n" + "=" * 60)
    print("🚨  SECURITY WARNING for Forked Users  🚨")
    print("-" * 60)
    print("⚠️  This is a PUBLIC repository.")
    print("🧠  Do NOT expose your BOT_TOKEN, API_ID, API_HASH, or cookies.txt.")
    print("💡  Always use Heroku Config Vars or a private .env file to store secrets.")
    print("🔒  Never commit sensitive data to your fork — anyone can steal it!")
    print("📢  Support: @MyAnieEnglishUpdates")
    print("=" * 60 + "\n")

    # Ensure download folder exists
    if not os.path.isdir(Config.DOWNLOAD_LOCATION):
        os.makedirs(Config.DOWNLOAD_LOCATION)

    # Load Plugins
    plugins = dict(root="plugins")

    # Initialize the Bot
    # FIXED: Changed variable name from 'Client' to 'app' to avoid conflict
    app = Client(
        name=Config.SESSION_NAME,  # Uses the session name from Config
        bot_token=Config.BOT_TOKEN,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        workers=100,               # Better concurrency
        upload_boost=True,         # Deprecated in newer Pyrogram but kept for compatibility
        sleep_threshold=300,
        plugins=plugins
    )

    print("🎊 I AM ALIVE 🎊  • Support @MyAnimeEnglishUpdates")
    
    # Run the bot
    app.run()
