import traceback
import datetime
import asyncio
import string
import random
import time
import os
import aiofiles
import aiofiles.os
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from plugins.database.database import db
from plugins.config import Config

broadcast_ids = {}

async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.value) # Fixed: usually e.value in newer pyrogram, or e.x in older
        return await send_msg(user_id, message) # FIXED: Added await here
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as e:
        return 500, f"{user_id} : {traceback.format_exc()}\n"

@Client.on_message(filters.private & filters.command('broadcast') & filters.reply)
async def broadcast_(c, m):
    # Security Check
    if m.from_user.id != Config.OWNER_ID:
        return

    # Validation: Ensure there is a message to broadcast
    if not m.reply_to_message:
        await m.reply_text("Please reply to a message to broadcast it.")
        return

    broadcast_msg = m.reply_to_message
    
    # Generate unique ID for this broadcast session
    while True:
        broadcast_id = ''.join([random.choice(string.ascii_letters) for i in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break

    out = await m.reply_text(
        text=f"Broadcast Started! You will be notified with a log file when completed."
    )
    
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    failed = 0
    success = 0
    
    broadcast_ids[broadcast_id] = dict(
        total=total_users,
        current=done,
        failed=failed,
        success=success
    )
    
    # Get all users (Assuming this yields a dict/object with 'id')
    all_users = await db.get_all_users()

    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        async for user in all_users:
            
            # Check if broadcast was cancelled externally
            if broadcast_ids.get(broadcast_id) is None:
                break

            sts, msg = await send_msg(
                user_id=int(user['id']),
                message=broadcast_msg
            )
            
            if msg is not None:
                await broadcast_log_file.write(msg)
            
            if sts == 200:
                success += 1
            else:
                failed += 1
            
            if sts == 400:
                # Clean up database
                await db.delete_user(user['id'])
            
            done += 1

            # Optimization: Update status every 20 users to save CPU/RAM
            if done % 20 == 0:
                if broadcast_ids.get(broadcast_id):
                    broadcast_ids[broadcast_id].update(
                        dict(
                            current=done,
                            failed=failed,
                            success=success
                        )
                    )
    
    # Cleanup status dict
    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)
    
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    
    await asyncio.sleep(3)
    await out.delete()
    
    if failed == 0:
        await m.reply_text(
            text=f"Broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True
        )
    else:
        await m.reply_document(
            document='broadcast.txt',
            caption=f"Broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True
        )
    
    # Cleanup log file
    if os.path.exists('broadcast.txt'):
        await aiofiles.os.remove('broadcast.txt')
