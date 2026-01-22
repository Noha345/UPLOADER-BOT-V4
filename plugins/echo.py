import logging
import asyncio
import json
import os
import time
import shutil
import random
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from plugins.config import Config
from plugins.script import Translation
from plugins.functions.verify import check_verification, get_token
from plugins.functions.forcesub import handle_force_subscribe
from plugins.functions.display_progress import humanbytes
from plugins.database.add import AddUser
from plugins.functions.ran_text import random_char

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

cookies_file = 'cookies.txt'

@Client.on_message(filters.private & filters.regex(pattern=".*http.*"))
async def echo(bot, update):
    # --- 1. Verification Check ---
    if update.from_user.id != Config.OWNER_ID:
        if Config.TRUE_OR_FALSE and not await check_verification(bot, update.from_user.id):
            verify_url = await get_token(bot, update.from_user.id, f"https://telegram.me/{Config.BOT_USERNAME}?start=")
            button = [
                [InlineKeyboardButton("✓⃝ Vᴇʀɪꜰʏ ✓⃝", url=verify_url)],
                [InlineKeyboardButton("🔆 Wᴀᴛᴄʜ Hᴏᴡ Tᴏ Vᴇʀɪꜰʏ 🔆", url=f"{Config.VERIFICATION}")]
            ]
            await update.reply_text(
                text="<b>Pʟᴇᴀsᴇ Vᴇʀɪꜰʏ Fɪʀsᴛ Tᴏ Usᴇ Mᴇ</b>",
                protect_content=True,
                reply_markup=InlineKeyboardMarkup(button)
            )
            return

    # --- 2. Log Channel Forwarding ---
    if Config.LOG_CHANNEL:
        try:
            log_message = await update.forward(Config.LOG_CHANNEL)
            log_info = (
                f"Message Sender Information\n"
                f"\nFirst Name: {update.from_user.first_name}"
                f"\nUser ID: {update.from_user.id}"
                f"\nUsername: @{update.from_user.username or ''}"
                f"\nUser Link: {update.from_user.mention}"
            )
            await log_message.reply_text(
                text=log_info,
                disable_web_page_preview=True,
                quote=True
            )
        except Exception as error:
            logger.error(f"Log Error: {error}")

    if not update.from_user:
        return await update.reply_text("I don't know about you sar :(")

    await AddUser(bot, update)

    # --- 3. Force Subscribe Check ---
    if Config.UPDATES_CHANNEL:
        fsub = await handle_force_subscribe(bot, update)
        if fsub == 400:
            return

    # --- 4. URL Extraction ---
    logger.info(update.from_user)
    url = update.text
    youtube_dl_username = None
    youtube_dl_password = None
    file_name = None

    if "|" in url:
        url_parts = url.split("|")
        if len(url_parts) == 2:
            url = url_parts[0]
            file_name = url_parts[1]
        elif len(url_parts) == 4:
            url = url_parts[0]
            file_name = url_parts[1]
            youtube_dl_username = url_parts[2]
            youtube_dl_password = url_parts[3]
    else:
        # Extract from entities if no pipes
        found_url = False
        if update.entities:
            for entity in update.entities:
                if entity.type == enums.MessageEntityType.TEXT_LINK:
                    url = entity.url
                    found_url = True
                    break
                elif entity.type == enums.MessageEntityType.URL:
                    o = entity.offset
                    l = entity.length
                    url = url[o:o + l]
                    found_url = True
                    break
    
    if url: url = url.strip()
    if file_name: file_name = file_name.strip()
    if youtube_dl_username: youtube_dl_username = youtube_dl_username.strip()
    if youtube_dl_password: youtube_dl_password = youtube_dl_password.strip()

    logger.info(f"Processing URL: {url}")

    # --- 5. Prepare yt-dlp Command ---
    use_cookies = os.path.exists(cookies_file)
    command_to_exec = [
        "yt-dlp",
        "--no-warnings",
        "--allow-dynamic-mpd",
        "--no-check-certificate",
        "-j",
        url
    ]

    if Config.HTTP_PROXY:
        command_to_exec.extend(["--proxy", Config.HTTP_PROXY])
    else:
        command_to_exec.extend(["--geo-bypass-country", "IN"])

    if use_cookies:
        command_to_exec.extend(["--cookies", cookies_file])
    if youtube_dl_username:
        command_to_exec.extend(["--username", youtube_dl_username])
    if youtube_dl_password:
        command_to_exec.extend(["--password", youtube_dl_password])

    # --- 6. Execute yt-dlp ---
    chk = await bot.send_message(
        chat_id=update.chat.id,
        text='Pʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʟɪɴᴋ ⌛',
        disable_web_page_preview=True,
        reply_to_message_id=update.id,
        parse_mode=enums.ParseMode.HTML
    )

    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    
    # Error Handling
    if e_response and "nonnumeric port" not in e_response:
        error_message = e_response.replace(
            "please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output.", ""
        )
        if "This video is only available for registered users." in error_message:
            error_message += Translation.SET_CUSTOM_USERNAME_PASSWORD
        
        await chk.delete()
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.NO_VOID_FORMAT_FOUND.format(str(error_message)),
            reply_to_message_id=update.id,
            disable_web_page_preview=True
        )
        return False

    # --- 7. Parse JSON and Build Keyboard ---
    if t_response:
        # Handle cases where multiple JSONs are returned (e.g., playlists), take the first one
        if "\n" in t_response:
            t_response, _ = t_response.split("\n", 1)
            
        try:
            response_json = json.loads(t_response)
        except json.JSONDecodeError as e:
            logger.error(f"JSON Decode Error: {e}")
            await chk.delete()
            await update.reply_text("Failed to parse video information.")
            return

        randem = random_char(5)
        save_ytdl_json_path = os.path.join(
            Config.DOWNLOAD_LOCATION, 
            f"{update.from_user.id}{randem}.json"
        )
        
        with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
            json.dump(response_json, outfile, ensure_ascii=False)

        inline_keyboard = []
        duration = response_json.get("duration")
        video_title = response_json.get("title", "Video")

        if "formats" in response_json:
            for formats in response_json["formats"]:
                format_id = formats.get("format_id")
                format_string = formats.get("format_note") or formats.get("format")
                
                if "DASH" in str(format_string).upper():
                    continue

                format_ext = formats.get("ext")
                size = formats.get('filesize') or formats.get('filesize_approx') or 0

                cb_string_video = f"video|{format_id}|{format_ext}|{randem}"
                
                # Filter valid formats
                if format_string and "audio only" not in format_string:
                    inline_keyboard.append([
                        InlineKeyboardButton(
                            f"📁 {format_string} {format_ext} {humanbytes(size)}",
                            callback_data=cb_string_video
                        )
                    ])
                else:
                    # Fallback for weird formats
                    inline_keyboard.append([
                        InlineKeyboardButton(
                            f"📁 Unknown ({humanbytes(size)})",
                            callback_data=cb_string_video
                        )
                    ])

            # Audio Options
            if duration is not None:
                inline_keyboard.append([
                    InlineKeyboardButton("🎵 ᴍᴘ𝟹 (64 ᴋʙᴘs)", callback_data=f"audio|64k|mp3|{randem}"),
                    InlineKeyboardButton("🎵 ᴍᴘ𝟹 (128 ᴋʙᴘs)", callback_data=f"audio|128k|mp3|{randem}")
                ])
                inline_keyboard.append([
                    InlineKeyboardButton("🎵 ᴍᴘ𝟹 (320 ᴋʙᴘs)", callback_data=f"audio|320k|mp3|{randem}")
                ])
                
            inline_keyboard.append([
                InlineKeyboardButton("🔒 ᴄʟᴏsᴇ", callback_data='close')
            ])
        
        else:
            # Fallback if no formats found but valid JSON
            format_id = response_json.get("format_id", "best")
            format_ext = response_json.get("ext", "mp4")
            cb_string_video = f"video|{format_id}|{format_ext}|{randem}"
            inline_keyboard.append([
                InlineKeyboardButton("📁 Document", callback_data=cb_string_video)
            ])

        await chk.delete()
        
        # FIXED: Replaced `Thumbnail` class object with video_title
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.FORMAT_SELECTION.format(video_title) + "\n" + Translation.SET_CUSTOM_USERNAME_PASSWORD,
            reply_markup=InlineKeyboardMarkup(inline_keyboard),
            disable_web_page_preview=True,
            reply_to_message_id=update.id
        )

    else:
        # Fallback for Direct Links / Non-numeric ports
        inline_keyboard = [
            [InlineKeyboardButton("📁 ᴍᴇᴅɪᴀ", callback_data="video=OFL=ENON")]
        ]
        await chk.delete(True)
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.FORMAT_SELECTION.format("File"),
            reply_markup=InlineKeyboardMarkup(inline_keyboard),
            disable_web_page_preview=True,
            reply_to_message_id=update.id
        )
