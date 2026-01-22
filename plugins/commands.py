import random
import os
import time
import psutil
import shutil
import string
import asyncio
from asyncio import TimeoutError

# Pyrogram
from pyrogram import Client, filters, types, errors
from pyrogram.types import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    Message, 
    CallbackQuery, 
    ForceReply
)
from pyrogram.errors import MessageNotModified

# Local Plugins
from plugins.config import Config
from plugins.script import Translation
from plugins.database.add import AddUser
from plugins.database.database import db
from plugins.functions.forcesub import handle_force_subscribe
from plugins.settings.settings import OpenSettings
from plugins.functions.verify import verify_user, check_token

# --- Your Bot Logic Goes Below ---
