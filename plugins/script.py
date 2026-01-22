import os
import re
import aiohttp
import aiofiles
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from plugins.config import Config

# ------------------------------------------------------------------
#  YOUR TRANSLATION CLASS
# ------------------------------------------------------------------
class Translation(object):
    START_TEXT = "👋 Hᴇʟʟᴏ {}\n\nⵊ Aᴍ Tᴇʟᴇɢʀᴀᴍ URL Uᴘʟᴏᴀᴅᴇʀ Bᴏᴛ.\n\n**Sᴇɴᴅ ᴍᴇ ᴀ ᴅɪʀᴇᴄᴛ ʟɪɴᴋ ᴀɴᴅ ɪ ᴡɪʟʟ ᴜᴘʟᴏᴀᴅ ɪᴛ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ ᴀs ᴀ ꜰɪʟᴇ/ᴠɪᴅᴇᴏ**"
    HELP_TEXT = "**Hᴏᴡ Tᴏ Usᴇ Tʜɪs Bᴏᴛ** 🤔\n\n𖣔 Sᴇɴᴅ ᴜʀʟ | Nᴇᴡ ɴᴀᴍᴇ.ᴍᴋᴠ\n𖣔 To download a page/playlist as file: `URL | file.m3u8` or `URL | page.html`"
    ABOUT_TEXT = "URL Uploader Bot V4"
    
    START_BUTTONS = InlineKeyboardMarkup([[InlineKeyboardButton('🛠️ SETTINGS', callback_data='OpenSettings')], [InlineKeyboardButton('⛔ CLOSE', callback_data='close')]])
    HELP_BUTTONS = InlineKeyboardMarkup([[InlineKeyboardButton('⛔ CLOSE', callback_data='close')]])
    ABOUT_BUTTONS = InlineKeyboardMarkup([[InlineKeyboardButton('⛔ CLOSE', callback_data='close')]])
    BUTTONS = InlineKeyboardMarkup([[InlineKeyboardButton('⛔ Close', callback_data='close')]])

    DOWNLOAD_START = "📥 Downloading... 📥\n\nFile Name: {}"
    UPLOAD_START = "📤 Uploading... 📤"
    AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS = "**DONE** 🥰\n\nDownloaded in: {}s\nUploaded in: {}s"
    NO_VOID_FORMAT_FOUND = "ERROR... <code>{}</code>"
    INCORRECT_REQUEST = "Eʀʀᴏʀ"
    DOWNLOAD_FAILED = "🔴 Eʀʀᴏʀ 🔴"
    TEXT = "Sᴇɴᴅ ᴍᴇ ʏᴏᴜʀ ᴄᴜsᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ"
    IFLONG_FILE_NAME = " Only 64 characters can be named . "
    RENAME_403_ERR = "Sorry. You are not permitted to rename this file."
    ABS_TEXT = " Please don't be selfish."
    FORMAT_SELECTION = "<b>Sᴇʟᴇᴄᴛ Yᴏᴜʀ Fᴏʀᴍᴀᴛ 👇</b>\n\nTitle: <b>{}</b>"
    FILE_NOT_FOUND = "Error, File not Found!!"
    FF_MPEG_DEL_ETED_CUSTOM_MEDIA = "✅ Media cleared succesfully."
    SAVED_CUSTOM_THUMB_NAIL = "**SAVED THUMBNAIL** ✅"
    DEL_ETED_CUSTOM_THUMB_NAIL = "**DELETED THUMBNAIL** ✅"
    NO_CUSTOM_THUMB_NAIL_FOUND = "ɴᴏ ᴄᴜsᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ"

# ------------------------------------------------------------------
#  HELPER: EXTRACT URL
# ------------------------------------------------------------------
def clean_url(text):
    url_pattern = re.compile(r'https?://\S+')
    match = url_pattern.search(text)
    if match:
        return match.group(0)
    return None

# ------------------------------------------------------------------
#  MAIN LOGIC
# ------------------------------------------------------------------

@Client.on_message(filters.private & (filters.regex(pattern=".*http.*") | filters.regex(pattern=".*magnet.*")))
async def echo(bot, update):
    
    if "Processing..." in update.text:
        return

    # 1. Parsing the URL and Filename
    raw_text = update.text.strip()
    custom_file_name = None
    youtube_dl_username = None
    youtube_dl_password = None

    if "|" in raw_text:
        parts = raw_text.split("|")
        raw_text = parts[0].strip()
        custom_file_name = parts[1].strip()
        if len(parts) > 2:
            youtube_dl_username = parts[2].strip()
            youtube_dl_password = parts[3].strip()

    url = clean_url(raw_text)
    if not url:
        return await update.reply_text("⚠️ Could not find a valid URL.")

    # -----------------------------------------------------------------
    # 🌐 RAW FILE MODE
    # -----------------------------------------------------------------
    if custom_file_name and custom_file_name.lower().endswith(('.html', '.htm', '.m3u8', '.txt', '.json')):
        msg = await update.reply_text(f"🌐 **Downloading Raw File...**\n<code>{url}</code>", disable_web_page_preview=True)
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        content = await resp.text()
                        async with aiofiles.open(custom_file_name, mode='w', encoding='utf-8') as f:
                            await f.write(content)
                        await msg.edit("📤 **Uploading File...**")
                        await update.reply_document(document=custom_file_name, caption=f"🔗 Source: {url}")
                        os.remove(custom_file_name)
                        await msg.delete()
                        return
                    else:
                        await msg.edit(f"❌ Error: Website returned status code {resp.status}")
                        return
        except Exception as e:
            await msg.edit(f"❌ **Raw File Download Error:** {str(e)}")
            return

    # -----------------------------------------------------------------
    # 🎥 VIDEO MODE
    # -----------------------------------------------------------------
    
    command_to_exec = [
        "yt-dlp", "-j", "--no-warnings", "--allow-dynamic-mpd",
        "--no-check-certificate", "--ignore-errors",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "--referer", "https://www.google.com/",
        "--geo-bypass", "--geo-bypass-country", "US",
        "--extractor-args", "generic:impersonate", 
        url
    ]

    if Config.HTTP_PROXY != "":
        command_to_exec.extend(["--proxy", Config.HTTP_PROXY])
    if youtube_dl_username:
        command_to_exec.extend(["--username", youtube_dl_username])
    if youtube_dl_password:
        command_to_exec.extend(["--password", youtube_dl_password])

    msg = await update.reply_text(f"Processing... 🔎\n<code>{url}</code>", disable_web_page_preview=True)
    
    try:
        from plugins.functions.help_uploadbot import DownLoadFile
        
        # ⚠️ CRITICAL FIX BELOW: 
        # 1. Removed 'update' (Arg 2) which was causing the Type Error.
        # 2. Shifted 'msg' to Arg 2 (Correct).
        # 3. Shifted 'custom_file_name' to Arg 3 (Correct).
        # 4. Added 'None' as Arg 4 (Placeholder for Cookies/ChunkSize) to satisfy 7-argument requirement.
        
        await DownLoadFile(url, msg, custom_file_name, None, command_to_exec, update.id, update.chat.id)
        
    except Exception as e:
        await msg.edit(Translation.NO_VOID_FORMAT_FOUND.format(str(e)))
