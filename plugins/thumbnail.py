import logging
import os
import random
from PIL import Image

# Pyrogram
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Hachoir for Metadata
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

# Local Plugins
from plugins.config import Config
from plugins.script import Translation
from plugins.database.add import AddUser
from plugins.database.database import db
from plugins.functions.forcesub import handle_force_subscribe
from plugins.functions.help_Nekmo_ffmpeg import take_screen_shot

logger = logging.getLogger(__name__)

@Client.on_message(filters.photo & filters.private)
async def save_photo(bot, update):
    await AddUser(bot, update)
    
    if Config.UPDATES_CHANNEL:
        fsub = await handle_force_subscribe(bot, update)
        if fsub == 400:
            return

    # Ensure download directory exists
    if not os.path.isdir(Config.DOWNLOAD_LOCATION):
        os.makedirs(Config.DOWNLOAD_LOCATION)

    download_location = os.path.join(
        Config.DOWNLOAD_LOCATION,
        str(update.from_user.id) + ".jpg"
    )
    
    # Download the photo
    await bot.download_media(
        message=update,
        file_name=download_location
    )
    
    # Update Database
    await db.set_thumbnail(update.from_user.id, thumbnail=update.photo.file_id)
    
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.SAVED_CUSTOM_THUMB_NAIL,
        reply_to_message_id=update.id
    )

@Client.on_message(filters.command(["delthumb"]) & filters.private)
async def delete_thumbnail(bot, update):
    await AddUser(bot, update)
    
    if Config.UPDATES_CHANNEL:
        fsub = await handle_force_subscribe(bot, update)
        if fsub == 400:
            return

    download_location = os.path.join(
        Config.DOWNLOAD_LOCATION,
        str(update.from_user.id) + ".jpg"
    )
    
    # Remove local file if exists
    try:
        if os.path.exists(download_location):
            os.remove(download_location)
    except Exception as e:
        logger.error(f"Error deleting thumbnail file: {e}")

    # Remove from Database
    await db.set_thumbnail(update.from_user.id, thumbnail=None)
    
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.DEL_ETED_CUSTOM_THUMB_NAIL,
        reply_to_message_id=update.id
    )

@Client.on_message(filters.command("showthumb") & filters.private)
async def viewthumbnail(bot, update):
    await AddUser(bot, update)

    if Config.UPDATES_CHANNEL:
        fsub = await handle_force_subscribe(bot, update)
        if fsub == 400:
            return
            
    thumbnail = await db.get_thumbnail(update.from_user.id)
    
    if thumbnail is not None:
        await bot.send_photo(
            chat_id=update.chat.id,
            photo=thumbnail,
            caption=f"YOUR THUMBNAIL 🏞",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🗑️ 𝙳𝙴𝙻𝙴𝚃𝙴 𝚃𝙷𝚄𝙼𝙱𝙽𝙰𝙸𝙻", callback_data="deleteThumbnail")]]
            ),
            reply_to_message_id=update.id
        )
    else:
        await update.reply_text(
            text=f"𝙽𝙾 𝚃𝙷𝚄𝙼𝙱𝙽𝙰𝙸𝙻 😐",
            reply_to_message_id=update.id
        )

# --- Helper Functions ---

async def Gthumb01(bot, update):
    """
    Downloads the custom thumbnail and resizes it for Document uploads.
    """
    thumb_image_path = os.path.join(Config.DOWNLOAD_LOCATION, str(update.from_user.id) + ".jpg")
    db_thumbnail = await db.get_thumbnail(update.from_user.id)
    
    if db_thumbnail is not None:
        try:
            thumbnail = await bot.download_media(message=db_thumbnail, file_name=thumb_image_path)
            # FIXED: Resize logic
            img = Image.open(thumbnail)
            img.convert("RGB")
            # Use thumbnail() to preserve aspect ratio, 320px is standard Telegram width
            img.thumbnail((320, 320)) 
            img.save(thumbnail, "JPEG")
            return thumbnail
        except Exception as e:
            logger.error(f"Error processing Gthumb01: {e}")
            return None
    else:
        return None

async def Gthumb02(bot, update, duration, download_directory):
    """
    Gets custom thumbnail, or takes a screenshot if no custom thumbnail exists.
    """
    thumb_image_path = os.path.join(Config.DOWNLOAD_LOCATION, str(update.from_user.id) + ".jpg")
    db_thumbnail = await db.get_thumbnail(update.from_user.id)
    
    if db_thumbnail is not None:
        return await bot.download_media(message=db_thumbnail, file_name=thumb_image_path)
    elif duration > 1:
        # Generate a random screenshot from the video
        return await take_screen_shot(
            download_directory, 
            os.path.dirname(download_directory), 
            random.randint(0, duration - 1)
        )
    else:
        return None

async def Mdata01(download_directory):
    width = 0
    height = 0
    duration = 0
    try:
        metadata = extractMetadata(createParser(download_directory))
        if metadata is not None:
            if metadata.has("duration"):
                duration = metadata.get('duration').seconds
            if metadata.has("width"):
                width = metadata.get("width")
            if metadata.has("height"):
                height = metadata.get("height")
    except Exception as e:
        logger.error(f"Error getting metadata 01: {e}")
        
    return width, height, duration

async def Mdata02(download_directory):
    width = 0
    duration = 0
    try:
        metadata = extractMetadata(createParser(download_directory))
        if metadata is not None:
            if metadata.has("duration"):
                duration = metadata.get('duration').seconds
            if metadata.has("width"):
                width = metadata.get("width")
    except Exception as e:
        logger.error(f"Error getting metadata 02: {e}")

    return width, duration

async def Mdata03(download_directory):
    try:
        metadata = extractMetadata(createParser(download_directory))
        if metadata is not None and metadata.has("duration"):
            return metadata.get('duration').seconds
    except Exception as e:
        logger.error(f"Error getting metadata 03: {e}")
    
    return 0
