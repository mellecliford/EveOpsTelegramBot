import os
import asyncio
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram import F
from aiogram.utils.chat_action import ChatActionSender
from downloader import download_video, download_audio
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# FIX 3: In-memory storage for URLs. 
# Telegram buttons fail if data is > 64 bytes (Long URLs crash the bot).
url_storage = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "EveOps Downloader Bot\n\n"
        "Send any link → get MP4 or MP3 instantly\n"
        "Zero watermarks • All platforms supported"
    )

@dp.message(F.text.regexp(r"https?://"))
async def handle_link(message: types.Message):
    url = message.text.strip()
    await message.reply("Analyzing link...")

    # Generate a short unique ID for this link
    link_id = str(uuid.uuid4())[:8]
    url_storage[link_id] = url

    # Store the ID in the button, not the full URL
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Video (MP4)", callback_data=f"mp4|{link_id}")],
        [InlineKeyboardButton(text="Audio (MP3)", callback_data=f"mp3|{link_id}")],
        [InlineKeyboardButton(text="Both", callback_data=f"both|{link_id}")]
    ])
    await message.answer("Choose format:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("mp4|") | F.data.startswith("mp3|") | F.data.startswith("both|"))
async def process_callback(callback: types.CallbackQuery):
    mode, link_id = callback.data.split("|", 1)
    
    # Retrieve the URL from storage using the ID
    url = url_storage.get(link_id)
    
    if not url:
        await callback.message.edit_text("❌ Link expired. Please send it again.")
        return

    await callback.message.edit_text(f"Downloading highest quality... (10–60s)")

    path = None
    try:
        # VIDEO DOWNLOAD
        if "mp4" in mode or "both" in mode:
            # Send 'uploading_video' action while processing
            async with ChatActionSender.upload_video(chat_id=callback.message.chat.id, bot=bot):
                path = await download_video(url)
                await callback.message.answer_video(FSInputFile(path), caption="EveOps • No watermarks")
                # Clean up immediately
                if os.path.exists(path):
                    os.remove(path)

        # AUDIO DOWNLOAD
        if "mp3" in mode or "both" in mode:
            async with ChatActionSender.upload_document(chat_id=callback.message.chat.id, bot=bot):
                path = await download_audio(url)
                await callback.message.answer_audio(FSInputFile(path), caption="EveOps • 320kbps MP3")
                # Clean up immediately
                if os.path.exists(path):
                    os.remove(path)

        await callback.message.delete()

    except Exception as e:
        error_msg = str(e)
        print(f"Error: {error_msg}") # Print to console for debugging
        await callback.message.edit_text(f"Failed: {error_msg[:100]}...") # Send short error to user
    
    finally:
        # Final cleanup safety net
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass

async def main():
    print("EveOps Bot ONLINE!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
