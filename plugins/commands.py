
from plugins.forcesub import ForceSub
import os
import sys
import asyncio
from database import db, mongodb_version
from config import Config, temp
from platform import python_version
from translation import Translation
from pyrogram import Client, filters, enums, __version__ as pyrogram_version
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaDocument, Message
import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
import time
import threading
import json
from codewithshubham.strings import strings

main_buttons = [[
        InlineKeyboardButton('🕷 ᴄᴏᴅᴇ ᴀʀᴛɪꜱᴀɴ', url='https://t.me/shubham_X_official')
        ],[
        InlineKeyboardButton('👨‍💻 ꜱᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/unreal_x_support'),
        InlineKeyboardButton('🔄 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/unreal_x_bot')
        ],[
        InlineKeyboardButton('🆘 ʜᴇʟᴘ', callback_data='help'),
        InlineKeyboardButton('ℹ️ ᴀʙᴏᴜᴛ', callback_data='about')
        ],[
        InlineKeyboardButton('⚙️ ꜱᴇᴛᴛɪɴɢꜱ', callback_data='settings#main')
        ]]

buttons = [[
        InlineKeyboardButton('🕸 ᴄᴏᴅᴇ ᴀʀᴛɪꜱᴀɴ', url='https://t.me/shubham_X_official'),
        InlineKeyboardButton('👀 ꜱᴏᴜʀᴄᴇ ᴄᴏᴅᴇ', url='https://t.me/shubham_X_official')
        ]]


#===================Start Function===================#

@Client.on_message(filters.private & filters.command(['start']))
async def start(client, message):
    user = message.from_user
    
    # Check for force subscription
    Fsub = await ForceSub(client, message)
    if Fsub == 400:
        return
    
    # Fetch the picture from the provided URL
    picture_url = "https://telegra.ph/file/c05c0889dcd0c1054de3f.jpg"
    
    # Send the picture with the start message
    await client.send_photo(
        chat_id=message.chat.id,
        photo=picture_url,
        caption=Translation.START_TXT.format(message.from_user.first_name),
        reply_markup=InlineKeyboardMarkup(main_buttons)
    )
    
    # Check if the user exists in the database and add if not
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)


#==================Restart Function==================#

@Client.on_message(filters.private & filters.command(['restart']) & filters.user(Config.BOT_OWNER_ID))
async def restart(client, message):
    msg = await message.reply_text(
        text="<i>Trying to restarting.....</i>"
    )
    await asyncio.sleep(5)
    await msg.edit("<i>Server restarted successfully ✅</i>")
    os.execl(sys.executable, sys.executable, *sys.argv)

#===================HELP Function===================#

@Client.on_message(filters.command('help'))
async def help(client, message):
    user = message.from_user
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
    
    # Fetch the picture from the provided URL
    picture_url = "https://telegra.ph/file/c05c0889dcd0c1054de3f.jpg"
    
    # Send the picture along with the help message
    await message.reply_photo(
        photo=picture_url,
        caption=Translation.HELP_TXT.format(message.from_user.first_name),
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    
#==================Callback Functions==================#

@Client.on_callback_query(filters.regex(r'^help'))
async def helpcb(bot, query):
    await query.message.edit_text(
        text=Translation.HELP_TXT,
        reply_markup=InlineKeyboardMarkup(
            [[
            InlineKeyboardButton('ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ ❓', callback_data='how_to_use')
            ],[
            InlineKeyboardButton('⚙️ sᴇᴛᴛɪɴɢs ', callback_data='settings#main'),
            InlineKeyboardButton('📜 sᴛᴀᴛᴜs ', callback_data='status')
            ],[
            InlineKeyboardButton('↩ ʙᴀᴄᴋ', callback_data='back')
            ]]
        ))

@Client.on_callback_query(filters.regex(r'^how_to_use'))
async def how_to_use(bot, query):
    await query.message.edit_text(
        text=Translation.HOW_USE_TXT,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('↩ Back', callback_data='help')]]),
        disable_web_page_preview=True
    )

@Client.on_callback_query(filters.regex(r'^back'))
async def back(bot, query):
    reply_markup = InlineKeyboardMarkup(main_buttons)
    await query.message.edit_text(
       reply_markup=reply_markup,
       text=Translation.START_TXT.format(
                query.from_user.first_name))

@Client.on_callback_query(filters.regex(r'^about'))
async def about(bot, query):
    await query.message.edit_text(
        text=Translation.ABOUT_TXT.format(my_name='Public Forward',python_version=python_version(),pyrogram_version=pyrogram_version,mongodb_version=await mongodb_version()),
        reply_markup=InlineKeyboardMarkup(
            [[
            InlineKeyboardButton('🕷 ᴄᴏᴅᴇ ᴀʀᴛɪꜱᴀɴ', url='https://t.me/shubham_X_official'),
            InlineKeyboardButton('👀 ꜱᴏᴜʀᴄᴇ ᴄᴏᴅᴇ', url='https://t.me/shubham_X_official')
            ],[
            InlineKeyboardButton('↩ ʙᴀᴄᴋ', callback_data='back')
            ]]
        ),
        disable_web_page_preview=True,
        parse_mode=enums.ParseMode.HTML,
                    )

@Client.on_callback_query(filters.regex(r'^status'))
async def status(bot, query):
    users_count, bots_count = await db.total_users_bots_count()
    total_channels = await db.total_channels()
    await query.message.edit_text(
        text=Translation.STATUS_TXT.format(users_count, bots_count, temp.forwardings, total_channels, temp.BANNED_USERS ),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('↩ Back', callback_data='help')]]),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True,
    )


# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    msg_type = get_message_type(msg)
    chat = message.chat.id
    if "Text" == msg_type:
        try:
            await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            return

    smsg = await client.send_message(message.chat.id, 'Downloading', reply_to_message_id=message.id)
    dosta = asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        os.remove(f'{message.id}downstatus.txt')
        
    except Exception as e:
        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)  
    
    upsta = asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg))

    if msg.caption:
        caption = msg.caption
    else:
        caption = None
            
    if "Document" == msg_type:
        try:
            ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
        except:
            ph_path = None
        
        try:
            await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        if ph_path != None: os.remove(ph_path)
        

    elif "Video" == msg_type:
        try:
            ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
        except:
            ph_path = None
        
        try:
            await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        if ph_path != None: os.remove(ph_path)

    elif "Animation" == msg_type:
        try:
            await client.send_animation(chat, file, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        

    elif "Sticker" == msg_type:
        try:
            await client.send_sticker(chat, file, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        

    elif "Voice" == msg_type:
        try:
            await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

    elif "Audio" == msg_type:
        try:
            ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
        except:
            ph_path = None

        try:
            await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])   
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        
        if ph_path != None: os.remove(ph_path)

    elif "Photo" == msg_type:
        try:
            await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
    
    if os.path.exists(f'{message.id}upstatus.txt'): 
        os.remove(f'{message.id}upstatus.txt')
        os.remove(file)
    await client.delete_messages(message.chat.id,[smsg.id])


# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass
        
