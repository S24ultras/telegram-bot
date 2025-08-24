#!/data/data/com.termux/files/usr/bin/bash
# ==========================================
# ✅ Prime Bot (Bot + Auto Uploader) One-Click Installer
# ==========================================

echo "🔄 Updating Termux..."
pkg update -y && pkg upgrade -y

echo "📦 Installing Python & dependencies..."
pkg install -y python tmux git
pip install --upgrade pip
pip install pyrogram tgcrypto

# Create bot folder
mkdir -p ~/primebot
cd ~/primebot

echo "📝 Generating bot.py..."
cat > bot.py << 'EOF'
import os
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===============================
# 🔹 Telegram Bot Credentials
# ===============================


# ===============================
# 🔹 Channel & Files
# ===============================
C

# ===============================
# 🔹 Owner/Admin
# ===============================


approved_users = {}   # {user_id: expiry_date}
pending_requests = {} # {user_id: requester_id}
uploaded_files = set()  # Track already uploaded files

# ===============================
# 🔹 Init Bot
# ===============================
bot = Client("prime_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ===============================
# 🔹 Check if user subscribed
# ===============================
async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ===============================
# 🔹 /start Command
# ===============================
@bot.on_message(filters.command("start"))
async def start_cmd(client, message):
    user_id = message.from_user.id

    if user_id == OWNER_ID:
        return await message.reply("👑 Welcome Admin! Direct Dolby access granted.")

    if user_id not in approved_users:
        return await message.reply("🚫 You are not approved yet.\nAsk Admin for approval.")

    expiry_date = approved_users[user_id]
    if datetime.now() > expiry_date:
        del approved_users[user_id]
        return await message.reply("⏳ Your plan expired. Contact Admin.")

    if not await is_subscribed(user_id):
        return await message.reply(
            "❌ You must join our Dolby Channel first.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
                [InlineKeyboardButton("✅ I Joined", callback_data="check_sub")]
            ])
        )

    await send_files(message)

# ===============================
# 🔹 Send Files Function
# ===============================
async def send_files(message):
    if os.path.exists(FOLDER_PATH):
        for filename in os.listdir(FOLDER_PATH):
            file_path = os.path.join(FOLDER_PATH, filename)
            if os.path.isfile(file_path):
                try:
                    await message.reply_document(
                        document=file_path,
                        caption=f"📌 {filename}"
                    )
                except Exception as e:
                    print(f"❌ Failed {filename} | {e}")
        await message.reply("✅ All Dolby files sent!")

# ===============================
# 🔹 /allow <user_id>
# ===============================
@bot.on_message(filters.command("allow"))
async def allow_request(client, message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Usage: `/allow <user_id>`")

    try:
        target_id = int(message.command[1])
    except:
        return await message.reply("❌ Invalid user ID format.")

    pending_requests[target_id] = message.from_user.id

    await bot.send_message(
        OWNER_ID,
        f"📩 Approval Request:\n\nRequester: `{message.from_user.id}`\nTarget User: `{target_id}`",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Approve", callback_data=f"approve_{target_id}")],
            [InlineKeyboardButton("❌ Reject", callback_data=f"reject_{target_id}")]
        ])
    )

    await message.reply("📨 Your approval request has been sent to Admin.")

# ===============================
# 🔹 Approve / Reject
# ===============================
@bot.on_callback_query(filters.regex("approve_"))
async def approve_user(client, callback_query):
    if callback_query.from_user.id != OWNER_ID:
        return await callback_query.answer("🚫 Not allowed", show_alert=True)

    target_id = int(callback_query.data.split("_")[1])
    expiry_date = datetime.now() + timedelta(days=28)
    approved_users[target_id] = expiry_date

    if target_id in pending_requests:
        del pending_requests[target_id]

    await callback_query.message.edit_text(
        f"✅ User `{target_id}` approved till {expiry_date.strftime('%d-%m-%Y %H:%M')}"
    )

    try:
        await bot.send_message(
            target_id,
            "🎉 Your request was approved!\n\n"
            "📢 Please join our Dolby Channel and then click '✅ I Joined' to verify.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
                [InlineKeyboardButton("✅ I Joined", callback_data="check_sub")]
            ])
        )
    except:
        pass

@bot.on_callback_query(filters.regex("reject_"))
async def reject_user(client, callback_query):
    if callback_query.from_user.id != OWNER_ID:
        return await callback_query.answer("🚫 Not allowed", show_alert=True)

    target_id = int(callback_query.data.split("_")[1])
    if target_id in pending_requests:
        del pending_requests[target_id]

    await callback_query.message.edit_text(f"❌ User `{target_id}` request rejected.")

# ===============================
# 🔹 Recheck Subscription
# ===============================
@bot.on_callback_query(filters.regex("check_sub"))
async def recheck(client, callback_query):
    user_id = callback_query.from_user.id

    if user_id == OWNER_ID:
        return await callback_query.message.reply("👑 Admin always verified!")

    if user_id in approved_users and await is_subscribed(user_id):
        await callback_query.message.reply("🎉 Verified! Sending Dolby files...")
        await send_files(callback_query.message)
    else:
        await callback_query.answer("❌ Still not subscribed!", show_alert=True)

# ===============================
# 🔹 /myplan Command
# ===============================
@bot.on_message(filters.command("myplan"))
async def myplan(client, message):
    user_id = message.from_user.id

    if user_id == OWNER_ID:
        return await message.reply("👑 You are Admin. Unlimited access!")

    if user_id not in approved_users:
        return await message.reply("🚫 You are not approved yet.")

    expiry = approved_users[user_id]
    await message.reply(f"📅 Your plan is valid till: {expiry.strftime('%d-%m-%Y %H:%M')}")

# ===============================
# 🔹 /list (Admin Only)
# ===============================
@bot.on_message(filters.command("list"))
async def list_users(client, message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("🚫 Only Admin can use this command.")

    if not approved_users:
        return await message.reply("📭 No active subscribers.")

    text = "📋 **Subscribers List:**\n\n"
    for uid, expiry in approved_users.items():
        text += f"👤 `{uid}` → Expires: {expiry.strftime('%d-%m-%Y %H:%M')}\n"

    await message.reply(text)

# ===============================
# 🔹 /remove <user_id> (Admin Only)
# ===============================
@bot.on_message(filters.command("remove"))
async def remove_user(client, message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("🚫 Only Admin can remove users.")

    if len(message.command) < 2:
        return await message.reply("⚠️ Usage: `/remove <user_id>`")

    try:
        target_id = int(message.command[1])
    except:
        return await message.reply("❌ Invalid user ID format.")

    if target_id in approved_users:
        del approved_users[target_id]

        try:
            await bot.ban_chat_member(CHANNEL_ID, target_id)
            await bot.unban_chat_member(CHANNEL_ID, target_id)
        except:
            pass

        await message.reply(f"🗑️ User `{target_id}` removed from bot and channel.")
        try:
            await bot.send_message(target_id, "🚫 Your access has been revoked by Admin.")
        except:
            pass
    else:
        await message.reply("❌ User not found in approved list.")

# ===============================
# 🔹 Auto Uploader (Background Task)
# ===============================
async def auto_upload():
    print("🚀 Auto Uploader Started...")
    await bot.send_message(CHANNEL_ID, "📤 Auto Uploader Started...")

    while True:
        if FOLDER_PATH.exists():
            for filename in os.listdir(FOLDER_PATH):
                file_path = FOLDER_PATH / filename
                if file_path.is_file() and file_path not in uploaded_files:
                    try:
                        print(f"📤 Uploading: {filename}")
                        await bot.send_document(
                            chat_id=CHANNEL_ID,
                            document=str(file_path),
                            caption=f"📌 {filename}"
                        )
                        uploaded_files.add(file_path)
                        print(f"✅ Uploaded: {filename}")
                    except Exception as e:
                        print(f"❌ Failed {filename} | {e}")
        await asyncio.sleep(10)

# ===============================
# 🔹 Run Bot + Auto Uploader
# ===============================
async def main():
    async with bot:
        asyncio.create_task(auto_upload())
        await asyncio.Event().wait()

if __name__ == "__main__":
    print("🤖 Prime Bot running with Auto Uploader...")
    asyncio.run(main())
EOF

echo "✅ Bot script created at ~/primebot/bot.py"
echo "➡️ Starting bot inside tmux session..."

tmux new -d -s primebot "cd ~/primebot && python bot.py"

echo "🎉 Bot started in background!"
echo "👉 To view logs: tmux attach -t primebot"
