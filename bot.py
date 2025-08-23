import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = 27445790
API_HASH = "9ba9db1e32788364afd9757ed5d7f1f5"
BOT_TOKEN = "7893773198:AAGlrAZ9pRZrZon-_zraNF8e6hK1u55UQeY"

CHANNEL_LINK = "https://t.me/+EdiH5HKvpyUyMzNl"
CHANNEL_USERNAME = "Dolby"

FOLDER_PATH = r"C:\Users\krish\Desktop\myfiles"

bot = Client("sub_check_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
async def start(client, message):
    ...
    # (rest of your code same as you gave me)
    ...

bot.run()
