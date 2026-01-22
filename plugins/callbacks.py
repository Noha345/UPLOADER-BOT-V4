import os
import logging
from pyrogram import Client, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant # FIXED: Added missing import

from plugins.functions.display_progress import progress_for_pyrogram, humanbytes
from plugins.config import Config
from plugins.dl_button import ddl_call_back
from plugins.button import youtube_dl_call_back
from plugins.settings.settings import OpenSettings
from plugins.script import Translation
from plugins.database.database import db

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@Client.on_callback_query()
async def button(bot, update):
    # --- Menu Navigation ---
    if update.data == "home":
        await update.message.edit(
            text=Translation.START_TEXT.format(update.from_user.mention),
            reply_markup=Translation.START_BUTTONS,
        )
    elif update.data == "help":
        await update.message.edit(
            text=Translation.HELP_TEXT,
            reply_markup=Translation.HELP_BUTTONS,
        )
    elif update.data == "about":
        await update.message.edit(
            text=Translation.ABOUT_TEXT,
            reply_markup=Translation.ABOUT_BUTTONS,
        )

    # --- Force Subscription Check ---
    elif "refreshForceSub" in update.data:
        if Config.UPDATES_CHANNEL:
            try:
                # Ensure channel ID is an integer if it starts with -100
                if str(Config.UPDATES_CHANNEL).startswith("-100"):
                    channel_chat_id = int(Config.UPDATES_CHANNEL)
                else:
                    channel_chat_id = Config.UPDATES_CHANNEL
                
                # Check Member Status
                user = await bot.get_chat_member(channel_chat_id, update.message.chat.id)
                
                if user.status == "kicked":
                    await update.message.edit(
                        text="Sorry Sir, You are Banned. Contact My [Support Group](https://t.me/NT_BOTS_SUPPORT)",
                        disable_web_page_preview=True
                    )
                    return
            
            except UserNotParticipant:
                # FIXED: Generate Invite Link dynamically because 'invite_link' variable was missing
                try:
                    invite_link = await bot.export_chat_invite_link(channel_chat_id)
                except Exception as e:
                    logger.error(f"Could not generate invite link: {e}")
                    await update.message.edit("Please contact admin. I cannot generate the invite link.")
                    return

                await update.message.edit(
                    text="**I like Your Smartness But Don't Be Oversmart! 😑**\n\n",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("🤖 Join Updates Channel", url=invite_link)
                            ],
                            [
                                InlineKeyboardButton("🔄 Refresh 🔄", callback_data="refreshForceSub")
                            ]
                        ]
                    )
                )
                return
            
            except Exception as e:
                logger.error(f"Force Sub Error: {e}")
                await update.message.edit(
                    text="Something Went Wrong. Contact My [Support Group](https://t.me/NT_BOTS_SUPPORT)",
                    disable_web_page_preview=True
                )
                return
        
        # If user is present or no channel set, return to Home
        await update.message.edit(
            text=Translation.START_TEXT.format(update.from_user.mention),
            reply_markup=Translation.START_BUTTONS,
        )

    # --- Settings & Tools ---
    elif update.data == "OpenSettings":
        await update.answer()
        await OpenSettings(update.message)
    
    elif update.data == "showThumbnail":
        thumbnail = await db.get_thumbnail(update.from_user.id)
        if not thumbnail:
            await update.answer("You didn't set any custom thumbnail!", show_alert=True)
        else:
            await update.answer()
            await bot.send_photo(
                update.message.chat.id, 
                thumbnail, 
                "Custom Thumbnail",
                reply_markup=types.InlineKeyboardMarkup([[
                    types.InlineKeyboardButton("Delete Thumbnail", callback_data="deleteThumbnail")
                ]])
            )
            
    elif update.data == "deleteThumbnail":
        await db.set_thumbnail(update.from_user.id, None)
        await update.answer("Okay, I deleted your custom thumbnail. Now I will apply default thumbnail.", show_alert=True)
        await update.message.delete(True)
        
    elif update.data == "setThumbnail":
        await update.message.edit(
            text=Translation.TEXT,
            reply_markup=Translation.BUTTONS,
            disable_web_page_preview=True
        )

    # --- Toggles (GenSS, Sample, UploadMode) ---
    elif update.data == "triggerGenSS":
        await update.answer()
        # Toggle Logic: if True make False, else True
        current_status = await db.get_generate_ss(update.from_user.id)
        await db.set_generate_ss(update.from_user.id, not current_status)
        await OpenSettings(update.message)

    elif update.data == "triggerGenSample":
        await update.answer()
        current_status = await db.get_generate_sample_video(update.from_user.id)
        await db.set_generate_sample_video(update.from_user.id, not current_status)
        await OpenSettings(update.message)

    elif update.data == "triggerUploadMode":
        await update.answer()
        current_status = await db.get_upload_as_doc(update.from_user.id)
        await db.set_upload_as_doc(update.from_user.id, not current_status)
        await OpenSettings(update.message)

    # --- Core Functionality ---
    elif "close" in update.data:
        await update.message.delete(True)

    elif "|" in update.data:
        await youtube_dl_call_back(bot, update)
    elif "=" in update.data:
        await ddl_call_back(bot, update)

    else:
        await update.message.delete()
