import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from plugins.config import Config
from plugins.script import Translation
from plugins.database.add import AddUser
from plugins.functions.forcesub import handle_force_subscribe

@Client.on_message(filters.command(["start"]) & filters.private)
async def start(bot, update):
    # 1. Add User to Database
    await AddUser(bot, update)

    # 2. Check Force Subscription (If enabled)
    if Config.UPDATES_CHANNEL:
        fsub = await handle_force_subscribe(bot, update)
        # If user hasn't joined, fsub returns 400, so we stop here
        if fsub == 400:
            return

    # 3. Send Start Message
    await update.reply_text(
        text=Translation.START_TEXT.format(update.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=Translation.START_BUTTONS
    )

@Client.on_message(filters.command(["help"]) & filters.private)
async def help_user(bot, update):
    await AddUser(bot, update)
    await update.reply_text(
        text=Translation.HELP_TEXT,
        disable_web_page_preview=True,
        reply_markup=Translation.HELP_BUTTONS
    )

@Client.on_message(filters.command(["about"]) & filters.private)
async def about_user(bot, update):
    await AddUser(bot, update)
    await update.reply_text(
        text=Translation.ABOUT_TEXT,
        disable_web_page_preview=True,
        reply_markup=Translation.ABOUT_BUTTONS
    )
