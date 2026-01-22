import logging
import asyncio
import aiohttp
import os
import time
import math
from datetime import datetime
from pyrogram import enums

# Local Plugins
from plugins.config import Config
from plugins.script import Translation
from plugins.thumbnail import Gthumb01, Gthumb02, Mdata01, Mdata02, Mdata03
from plugins.database.database import db
from plugins.functions.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter

# Logging Setup
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


async def ddl_call_back(bot, update):
    logger.info(update)
    cb_data = update.data
    
    # Parse Callback Data
    try:
        tg_send_type, youtube_dl_format, youtube_dl_ext = cb_data.split("=")
    except ValueError:
        # Handle cases where format might be missing
        tg_send_type = "video"
        youtube_dl_format = "best"
        youtube_dl_ext = "mp4"

    thumb_image_path = os.path.join(Config.DOWNLOAD_LOCATION, f"{update.from_user.id}.jpg")
    
    # --- Parse URL ---
    youtube_dl_url = update.message.reply_to_message.text
    custom_file_name = os.path.basename(youtube_dl_url)
    
    if "|" in youtube_dl_url:
        url_parts = youtube_dl_url.split("|")
        if len(url_parts) == 2:
            youtube_dl_url = url_parts[0]
            custom_file_name = url_parts[1]
        else:
            # Fallback to entity parsing
            for entity in update.message.reply_to_message.entities:
                if entity.type == enums.MessageEntityType.TEXT_LINK:
                    youtube_dl_url = entity.url
                elif entity.type == enums.MessageEntityType.URL:
                    o = entity.offset
                    l = entity.length
                    youtube_dl_url = youtube_dl_url[o:o + l]
    else:
        # Entity parsing if no pipe
        if update.message.reply_to_message.entities:
            for entity in update.message.reply_to_message.entities:
                if entity.type == enums.MessageEntityType.TEXT_LINK:
                    youtube_dl_url = entity.url
                elif entity.type == enums.MessageEntityType.URL:
                    o = entity.offset
                    l = entity.length
                    youtube_dl_url = youtube_dl_url[o:o + l]
    
    # Cleanup strings
    if youtube_dl_url: youtube_dl_url = youtube_dl_url.strip()
    if custom_file_name: custom_file_name = custom_file_name.strip()

    logger.info(f"URL: {youtube_dl_url}")
    logger.info(f"File: {custom_file_name}")

    # --- Start Download Process ---
    start = datetime.now()
    await update.message.edit_caption(
        caption=Translation.DOWNLOAD_START,
        parse_mode=enums.ParseMode.HTML
    )

    tmp_directory = os.path.join(Config.DOWNLOAD_LOCATION, str(update.from_user.id))
    os.makedirs(tmp_directory, exist_ok=True)
    download_directory = os.path.join(tmp_directory, custom_file_name)

    async with aiohttp.ClientSession() as session:
        c_time = time.time()
        try:
            download_success = await download_coroutine(
                bot,
                session,
                youtube_dl_url,
                download_directory,
                update.message.chat.id,
                update.message.id,
                c_time
            )
            if not download_success:
                return # Stop if download failed/cancelled
                
        except asyncio.TimeoutError:
            await bot.edit_message_text(
                text=Translation.SLOW_URL_DECED,
                chat_id=update.message.chat.id,
                message_id=update.message.id
            )
            return False
        except Exception as e:
            logger.error(f"Download Error: {e}")
            await update.message.edit_caption(caption=f"Download Error: {e}")
            return False

    # --- Check File ---
    if os.path.exists(download_directory):
        end_one = datetime.now()
        await update.message.edit_caption(
            caption=Translation.UPLOAD_START,
            parse_mode=enums.ParseMode.HTML
        )
        
        # Verify Size
        try:
            file_size = os.stat(download_directory).st_size
        except FileNotFoundError:
            # Fallback if file extension changed during download (unlikely for DDL but possible)
            download_directory = os.path.splitext(download_directory)[0] + ".mkv"
            if os.path.exists(download_directory):
                file_size = os.stat(download_directory).st_size
            else:
                await update.message.edit_caption(caption="File not found after download.")
                return

        if file_size > Config.TG_MAX_FILE_SIZE:
            await update.message.edit_caption(
                caption=Translation.RCHD_TG_API_LIMIT,
                parse_mode=enums.ParseMode.HTML
            )
            return

        # --- Upload Logic ---
        start_time = time.time()
        description = Translation.CUSTOM_CAPTION_UL_FILE
        thumbnail = None

        # 1. Check Forced Document Setting
        is_force_doc = await db.get_upload_as_doc(update.from_user.id)
        
        if is_force_doc:
            thumbnail = await Gthumb01(bot, update)
            await update.message.reply_document(
                document=download_directory,
                thumb=thumbnail,
                caption=description,
                parse_mode=enums.ParseMode.HTML,
                progress=progress_for_pyrogram,
                progress_args=(Translation.UPLOAD_START, update.message, start_time)
            )
        
        # 2. Check Request Type (Audio/VM/Video)
        elif tg_send_type == "audio":
            duration = await Mdata03(download_directory)
            thumbnail = await Gthumb01(bot, update)
            await update.message.reply_audio(
                audio=download_directory,
                caption=description,
                parse_mode=enums.ParseMode.HTML,
                duration=duration,
                thumb=thumbnail,
                progress=progress_for_pyrogram,
                progress_args=(Translation.UPLOAD_START, update.message, start_time)
            )
            
        elif tg_send_type == "vm":
            width, duration = await Mdata02(download_directory)
            thumbnail = await Gthumb02(bot, update, duration, download_directory)
            await update.message.reply_video_note(
                video_note=download_directory,
                duration=duration,
                length=width,
                thumb=thumbnail,
                progress=progress_for_pyrogram,
                progress_args=(Translation.UPLOAD_START, update.message, start_time)
            )
            
        else:
            # Default to Video
            width, height, duration = await Mdata01(download_directory)
            thumb_image_path = await Gthumb02(bot, update, duration, download_directory)
            thumbnail = thumb_image_path
            await update.message.reply_video(
                video=download_directory,
                caption=description,
                duration=duration,
                width=width,
                height=height,
                supports_streaming=True,
                parse_mode=enums.ParseMode.HTML,
                thumb=thumb_image_path,
                progress=progress_for_pyrogram,
                progress_args=(Translation.UPLOAD_START, update.message, start_time)
            )

        # --- Cleanup ---
        end_two = datetime.now()
        time_taken_for_download = (end_one - start).seconds
        time_taken_for_upload = (end_two - end_one).seconds
        
        try:
            os.remove(download_directory)
            if thumbnail and os.path.exists(thumbnail):
                os.remove(thumbnail)
        except Exception:
            pass

        await update.message.edit_caption(
            caption=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(time_taken_for_download, time_taken_for_upload),
            parse_mode=enums.ParseMode.HTML
        )
    else:
        await update.message.edit_caption(
            caption=Translation.NO_VOID_FORMAT_FOUND.format("Incorrect Link or Download Failed"),
            parse_mode=enums.ParseMode.HTML
        )

async def download_coroutine(bot, session, url, file_name, chat_id, message_id, start_time):
    downloaded = 0
    display_message = ""
    last_update_time = time.time()
    
    try:
        async with session.get(url, timeout=Config.PROCESS_MAX_TIMEOUT) as response:
            if response.status != 200:
                await bot.edit_message_text(chat_id, message_id, text=f"Link Error: {response.status}")
                return False

            total_length = int(response.headers.get("Content-Length", 0))
            content_type = response.headers.get("Content-Type", "")
            
            if "text" in content_type and total_length < 500:
                return False # Likely an error page

            await bot.edit_message_text(
                chat_id,
                message_id,
                text=f"Initiating Download\nURL: {url}\nFile Size: {humanbytes(total_length)}"
            )

            with open(file_name, "wb") as f_handle:
                while True:
                    chunk = await response.content.read(Config.CHUNK_SIZE)
                    if not chunk:
                        break
                    f_handle.write(chunk)
                    downloaded += len(chunk)
                    
                    # --- FIXED PROGRESS UPDATE LOGIC ---
                    now = time.time()
                    # Update only every 5 seconds OR at 100%
                    if (now - last_update_time) > 5 or (total_length > 0 and downloaded == total_length):
                        last_update_time = now
                        
                        if total_length > 0:
                            percentage = downloaded * 100 / total_length
                            speed = downloaded / (now - start_time)
                            elapsed_time = round(now - start_time) * 1000
                            time_to_completion = round((total_length - downloaded) / speed) * 1000 if speed > 0 else 0
                            estimated_total_time = elapsed_time + time_to_completion
                            
                            status_text = f"**Download Status**\nURL: {url}\nFile Size: {humanbytes(total_length)}\nDownloaded: {humanbytes(downloaded)}\nETA: {TimeFormatter(estimated_total_time)}"
                        else:
                             status_text = f"**Download Status**\nDownloaded: {humanbytes(downloaded)}"

                        if status_text != display_message:
                            try:
                                await bot.edit_message_text(chat_id, message_id, text=status_text)
                                display_message = status_text
                            except Exception:
                                pass # Ignore edit errors (floodwait handled by pyrogram usually)
            
            return True # Success
    except Exception as e:
        logger.error(f"Download Exception: {e}")
        return False
