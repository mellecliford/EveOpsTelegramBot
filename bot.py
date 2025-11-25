import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram import F
from downloader import download_video, download_audio
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🔥 EveOps Downloader Bot 🔥\n\n"
        "Send me any link from:\n"
        "YouTube • TikTok • Instagram • Facebook\n"
        "Twitter/X • Reddit • Pinterest • Vimeo • Twitch clips\n\n"
        "I’ll give you the highest quality download — no watermarks ever."
    )

@dp.message(F.text.regexp(r"https?://"))
async def handle_link(message: types.Message):
    url = message.text.strip()
    await message.reply("⏳ Analyzing link...")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎥 Video (MP4)", callback_data=f"mp4|{url}")],
        [InlineKeyboardButton(text="🎵 Audio (MP3)", callback_data=f"mp3|{url}")],
        [InlineKeyboardButton(text="📦 Both", callback_data=f"both|{url}")]
    ])
    await message.answer("✅ Link detected! Choose format:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("mp4|") | F.data.startswith("mp3|") | F.data.startswith("both|"))
async def process_callback(callback: types.CallbackQuery):
    mode, url = callback.data.split("|", 1)
    await callback.message.edit_text("⬇️ Downloading in highest quality... (10–60s)")

    try:
        if "mp4" in mode or "both" in mode:
            path = await download_video(url)
            await callback.message.answer_chat_action("upload_video")
            await callback.message.answer_video(FSInputFile(path), caption="EveOps Downloader • No watermarks")
            os.remove(path)

        if "mp3" in mode or "both" in mode:
            path = await download_audio(url)
            await callback.message.answer_chat_action("upload_document")
            await callback.message.answer_audio(FSInputFile(path), caption="EveOps Downloader • 320kbps")
            os.remove(path)

        await callback.message.delete()
    except Exception as e:
        await callback.message.edit_text(f"❌ Failed: {str(e)}\nProbably private, deleted, or age-restricted.")

async def main():
    print("EveOps Bot is now ONLINE!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())