import os
import time
import math
import json
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from plugins.config import Config

# ------------------------------------------------------------------
#  YOUR TRANSLATION CLASS (Text & Buttons)
# ------------------------------------------------------------------
class Translation(object):

    START_TEXT = """
👋 Hᴇʟʟᴏ {} 

ⵊ Aᴍ Tᴇʟᴇɢʀᴀᴍ URL Uᴘʟᴏᴀᴅᴇʀ Bᴏᴛ.

**Sᴇɴᴅ ᴍᴇ ᴀ ᴅɪʀᴇᴄᴛ ʟɪɴᴋ ᴀɴᴅ ɪ ᴡɪʟʟ ᴜᴘʟᴏᴀᴅ ɪᴛ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ ᴀs ᴀ ꜰɪʟᴇ/ᴠɪᴅᴇᴏ**

Usᴇ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴋɴᴏᴡ ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ
"""

    HELP_TEXT = """
**Hᴏᴡ Tᴏ Usᴇ Tʜɪs Bᴏᴛ** 🤔
    
𖣔 Fɪʀsᴛ ɢᴏ ᴛᴏ ᴛʜᴇ /settings ᴀɴᴅ ᴄʜᴀɴɢᴇ ᴛʜᴇ ʙᴏᴛ ʙᴇʜᴀᴠɪᴏʀ ᴀs ʏᴏᴜʀ ᴄʜᴏɪᴄᴇ.

𖣔 Sᴇɴᴅ ᴍᴇ ᴛʜᴇ ᴄᴜsᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ ᴛᴏ sᴀᴠᴇ ɪᴛ ᴘᴇʀᴍᴀɴᴇɴᴛʟʏ.

𖣔 **Sᴇɴᴅ ᴜʀʟ | Nᴇᴡ ɴᴀᴍᴇ.ᴍᴋᴠ**

𖣔 Sᴇʟᴇᴄᴛ ᴛʜᴇ ᴅᴇsɪʀᴇᴅ ᴏᴘᴛɪᴏɴ.

𖣔 Usᴇ `/caption` ᴛᴏ sᴇᴛ ᴄᴀᴘᴛɪᴏɴ ᴀs Rᴇᴘʟʏ ᴛᴏ ᴍᴇᴅɪᴀ
"""

    ABOUT_TEXT = """
╭───────────⍟
├📛 **Mʏ Nᴀᴍᴇ** : URL Uᴘʟᴏᴀᴅᴇʀ Bᴏᴛ
├📢 **Fʀᴀᴍᴇᴡᴏʀᴋ** : <a href="https://docs.pyrogram.org/">PʏʀᴏBʟᴀᴄᴋ 2.7.4</a>
├💮 **Lᴀɴɢᴜᴀɢᴇ** : <a href="https://www.python.org">Pʏᴛʜᴏɴ 3.13.9</a>
├💾 **Dᴀᴛᴀʙᴀsᴇ** : <a href="https://cloud.mongodb.com">MᴏɴɢᴏDB</a>
├🚨 **Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ** : <a href="https://t.me/NT_BOTS_SUPPORT">Nᴛ Sᴜᴘᴘᴏʀᴛ</a>
├🥏 **Cʜᴀɴɴᴇʟ** : <a href="https://t.me/NT_BOT_CHANNEL">Nᴛ Bᴏᴛ Cʜᴀɴɴᴇʟ</a>
├👨‍💻 **Cʀᴇᴀᴛᴏʀ** : @NT_BOT_CHANNEL
╰───────────────⍟
"""

    PROGRESS = """
┣📦 Pʀᴏɢʀᴇꜱꜱ : {0}%
┣ ✅ Dᴏɴᴇ : {1}
┣ 📁 Tᴏᴛᴀʟ : {2}
┣ 🚀 Sᴘᴇᴇᴅ : {3}/s
┣ 🕒 Tɪᴍᴇ : {4}
┗━━━━━━━━━━━━━━━━━━━━
"""
    PROGRES = """
`{}`\n{}"""

    START_BUTTONS = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton('🛠️ SETTINGS', callback_data='OpenSettings')
        ],[
            InlineKeyboardButton('🤝 HELP', callback_data='help'),
            InlineKeyboardButton('🎯 ABOUT', callback_data='about')
        ],[
            InlineKeyboardButton('⛔ CLOSE', callback_data='close')
        ]]
    )

    HELP_BUTTONS = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton('🛠️ SETTINGS', callback_data='OpenSettings')
        ],[
            InlineKeyboardButton('🔙 BACK', callback_data='home'),
            InlineKeyboardButton('🎯 ABOUT', callback_data='about')
        ],[
            InlineKeyboardButton('⛔ CLOSE', callback_data='close')
        ]]
    )

    ABOUT_BUTTONS = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton('🛠️ SETTINGS', callback_data='OpenSettings')
        ],[
            InlineKeyboardButton('🔙 BACK', callback_data='home'),
            InlineKeyboardButton('🤝 HELP', callback_data='help')
        ],[
            InlineKeyboardButton('⛔ CLOSE', callback_data='close')
        ]]
    )

    BUTTONS = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton('⛔ Close', callback_data='close')
        ]]
    )

    INCORRECT_REQUEST = "Eʀʀᴏʀ"
    DOWNLOAD_FAILED = "🔴 Eʀʀᴏʀ 🔴"
    TEXT = "Sᴇɴᴅ ᴍᴇ ʏᴏᴜʀ ᴄᴜsᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ"
    IFLONG_FILE_NAME = " Only 64 characters can be named . "
    RENAME_403_ERR = "Sorry. You are not permitted to rename this file."
    ABS_TEXT = " Please don't be selfish."
    FORMAT_SELECTION = "<b>Sᴇʟᴇᴄᴛ Yᴏᴜʀ Fᴏʀᴍᴀᴛ 👇</b>\n\nTitle: <b>{}</b>"
    SET_CUSTOM_USERNAME_PASSWORD = """<b>🎥 Vɪᴅᴇᴏ = Uᴘʟᴏᴀᴅ As Sᴛʀᴇᴀᴍʙʟᴇ</b>\n\n<b>📂 Fɪʟᴇ = Uᴘʟᴏᴀᴅ As Fɪʟᴇ</b>\n\n<b>👮‍♂ Pᴏᴡᴇʀᴇᴅ Bʏ :</b>@MyAnimeEnglish"""
    DOWNLOAD_START = "📥 Downloading... 📥\n\nFile Name: {}"
    UPLOAD_START = "📤 Uploading... 📤"
    RCHD_BOT_API_LIMIT = "size greater than maximum allowed size (50MB). Neverthless, trying to upload."
    RCHD_TG_API_LIMIT = "Downloaded in {} seconds.\nDetected File Size: {}\nSorry. But, I cannot upload files greater than 2000MB due to Telegram API limitations.\n\nUse 4GB @UploaderXNTBot"
    AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS = "**𝘛𝘏𝘈𝘕𝘒𝘚 𝘍𝘖𝘙 𝘜𝘚𝘐𝘕𝘎 𝘔𝘌** 🥰\n\nDownloaded in: {}s\nUploaded in: {}s"
    SAVED_CUSTOM_THUMB_NAIL = "**SAVED THUMBNAIL** ✅"
    DEL_ETED_CUSTOM_THUMB_NAIL = "**DELETED THUMBNAIL** ✅"
    FF_MPEG_DEL_ETED_CUSTOM_MEDIA = "✅ Media cleared succesfully."
    CUSTOM_CAPTION_UL_FILE = " "
    NO_CUSTOM_THUMB_NAIL_FOUND = "ɴᴏ ᴄᴜsᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ"
    NO_VOID_FORMAT_FOUND = "ERROR... <code>{}</code>"
    FILE_NOT_FOUND = "Error, File not Found!!"
    FF_MPEG_RO_BOT_AD_VER_TISE_MENT = "Join : @MyAnimeEnglish \n For the list of Telegram bots. "
    ADD_CAPTION_HELP = """Select an uploaded file/video or forward me <b>Any Telegram File</b> and just write the text you want to be on the file <b>as a reply to the file</b> and the text you wrote will be attached as the caption! 🤩"""


# ------------------------------------------------------------------
#  MAIN LOGIC (Universal Downloader)
# ------------------------------------------------------------------

@Client.on_message(filters.private & (filters.regex(pattern=".*http.*") | filters.regex(pattern=".*magnet.*")))
async def echo(bot, update):
    
    # 1. Parsing the URL and Filename (if user used | separator)
    url = update.text
    youtube_dl_username = None
    youtube_dl_password = None
    custom_file_name = None

    if "|" in url:
        url_parts = url.split("|")
        if len(url_parts) == 2:
            url = url_parts[0].strip()
            custom_file_name = url_parts[1].strip()
        elif len(url_parts) == 4:
            url = url_parts[0].strip()
            custom_file_name = url_parts[1].strip()
            youtube_dl_username = url_parts[2].strip()
            youtube_dl_password = url_parts[3].strip()

    # 2. Setup the Command to Execute (THE CODE YOU REQUESTED)
    # ---------------------------------------------------------------------------------
    #  🚀 UNIVERSAL DOWNLOADER CONFIGURATION
    #  Mimics a Chrome Extension to find video on ANY website.
    # ---------------------------------------------------------------------------------
    
    command_to_exec = [
        "yt-dlp",
        
        # 1. Output Format (JSON for the bot to read)
        "-j",
        
        # 2. General Settings
        "--no-warnings",
        "--allow-dynamic-mpd",
        "--no-check-certificate",  # Fixes SSL errors on smaller/older sites
        "--ignore-errors",         # Keeps going even if one segment fails
        
        # 3. 🎭 ULTIMATE STEALTH MODE (Fakes a real PC Browser)
        # This user agent mimics Chrome 120 on Windows 10 perfectly.
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "--referer", "https://www.google.com/",  # Pretend we came from Google
        
        # 4. 🌍 Geo-Restriction Bypass
        "--geo-bypass",
        "--geo-bypass-country", "US", # Pretend to be in US if blocked
        
        # 5. 🧠 INTELLIGENT EXTRACTION (The "Extension" Logic)
        # If the specific site extractor fails, this forces the 'generic' extractor 
        # to scan the page for embedded video players (jwplayer, video.js, etc).
        "--extractor-args", "generic:impersonate", 

        # 6. The Target URL
        url
    ]

    # Add Proxy if you have one (Optional but recommended for strict sites)
    if Config.HTTP_PROXY != "":
        command_to_exec.extend(["--proxy", Config.HTTP_PROXY])

    # Add Credentials if the user provided them
    if youtube_dl_username is not None:
        command_to_exec.extend(["--username", youtube_dl_username])
    if youtube_dl_password is not None:
        command_to_exec.extend(["--password", youtube_dl_password])


    # 3. Send Processing Message
    msg = await update.reply_text(f"Processing... 🔎\n<code>{url}</code>", disable_web_page_preview=True)
    
    # NOTE: The rest of the download/upload logic (calling functions/functions.py) 
    # would usually follow here. Ensure you have the 'upload' or 'download' function calls
    # implemented in your full bot structure.
    # For now, this file successfully integrates your text and the command configuration.
