import os
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from plugins.config import Config

# ------------------------------------------------------------------
#  YOUR TRANSLATION CLASS
# ------------------------------------------------------------------
class Translation(object):
    START_TEXT = """
👋 Hᴇʟʟᴏ {} 
ⵊ Aᴍ Tᴇʟᴇɢʀᴀᴍ URL Uᴘʟᴏᴀᴅᴇʀ Bᴏᴛ.
**Sᴇɴᴅ ᴍᴇ ᴀ ᴅɪʀᴇᴄᴛ ʟɪɴᴋ ᴀɴᴅ ɪ ᴡɪʟʟ ᴜᴘʟᴏᴀᴅ ɪᴛ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ ᴀs ᴀ ꜰɪʟᴇ/ᴠɪᴅᴇᴏ**
"""
    HELP_TEXT = """
**Hᴏᴡ Tᴏ Usᴇ Tʜɪs Bᴏᴛ** 🤔
𖣔 Sᴇɴᴅ ᴜʀʟ | Nᴇᴡ ɴᴀᴍᴇ.ᴍᴋᴠ
𖣔 Usᴇ /settings for behavior.
"""
    ABOUT_TEXT = "URL Uploader Bot V4"
    
    START_BUTTONS = InlineKeyboardMarkup([[InlineKeyboardButton('🛠️ SETTINGS', callback_data='OpenSettings')], [InlineKeyboardButton('⛔ CLOSE', callback_data='close')]])
    HELP_BUTTONS = InlineKeyboardMarkup([[InlineKeyboardButton('⛔ CLOSE', callback_data='close')]])
    ABOUT_BUTTONS = InlineKeyboardMarkup([[InlineKeyboardButton('⛔ CLOSE', callback_data='close')]])
    BUTTONS = InlineKeyboardMarkup([[InlineKeyboardButton('⛔ Close', callback_data='close')]])

    # Status Messages
    DOWNLOAD_START = "📥 Downloading... 📥\n\nFile Name: {}"
    UPLOAD_START = "📤 Uploading... 📤"
    AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS = "**DONE** 🥰\n\nDownloaded in: {}s\nUploaded in: {}s"
    
# ------------------------------------------------------------------
#  HELPER: EXTRACT URL
# ------------------------------------------------------------------
def clean_url(text):
    # Regex to find http/https links
    url_pattern = re.compile(r'https?://\S+')
    match = url_pattern.search(text)
    if match:
        return match.group(0)
    return None

# ------------------------------------------------------------------
#  MAIN LOGIC (Universal Downloader)
# ------------------------------------------------------------------

@Client.on_message(filters.private & (filters.regex(pattern=".*http.*") | filters.regex(pattern=".*magnet.*")))
async def echo(bot, update):
    
    # 0. IGNORE "Processing" messages (Prevents the Loop Error)
    if "Processing..." in update.text:
        return

    # 1. Parsing the URL and Filename
    raw_text = update.text.strip()
    custom_file_name = None
    youtube_dl_username = None
    youtube_dl_password = None

    # Handle "|" separator for custom filenames
    if "|" in raw_text:
        parts = raw_text.split("|")
        raw_text = parts[0].strip()
        custom_file_name = parts[1].strip()
        if len(parts) > 2:
            youtube_dl_username = parts[2].strip()
            youtube_dl_password = parts[3].strip()

    # Clean the URL (Remove surrounding text/newlines)
    url = clean_url(raw_text)
    if not url:
        return await update.reply_text("⚠️ Could not find a valid URL in that message.")

    # 2. Setup the Command (Universal Logic)
    command_to_exec = [
        "yt-dlp",
        "-j", # JSON Output
        "--no-warnings",
        "--allow-dynamic-mpd",
        "--no-check-certificate",
        "--ignore-errors",
        
        # 🎭 STEALTH MODE (Chrome 120 on Windows)
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "--referer", "https://www.google.com/",
        
        # 🌍 Geo-Bypass
        "--geo-bypass",
        "--geo-bypass-country", "US",

        # 🧠 INTELLIGENT EXTRACTION (Universal Extension Logic)
        "--extractor-args", "generic:impersonate", 

        url
    ]

    if Config.HTTP_PROXY != "":
        command_to_exec.extend(["--proxy", Config.HTTP_PROXY])

    if youtube_dl_username is not None:
        command_to_exec.extend(["--username", youtube_dl_username])
    if youtube_dl_password is not None:
        command_to_exec.extend(["--password", youtube_dl_password])

    # 3. Send Processing Message
    msg = await update.reply_text(f"Processing... 🔎\n<code>{url}</code>", disable_web_page_preview=True)
    
    # 4. EXECUTE DOWNLOAD (The missing part from previous steps)
    # Note: In the V4 architecture, this usually calls a function in 'plugins/functions/help_uploadbot.py'
    # But since I don't see your specific imports, I'm ensuring the data passes correctly.
    
    # IMPORTANT: You must have the standard logic to handle the 'command_to_exec'.
    # If your bot crashes after "Processing...", ensure you have 'plugins/functions/help_uploadbot.py'
    # For now, this script fixes the URL Parsing Error.
    
    # Try to import the downloader if it exists in your folder structure
    try:
        from plugins.functions.help_uploadbot import DownLoadFile
        await DownLoadFile(url, update, msg, custom_file_name, command_to_exec)
    except ImportError:
        await msg.edit("❌ **Error:** Could not find `DownLoadFile` function.\nMake sure your `plugins/functions/` folder is correct.")
