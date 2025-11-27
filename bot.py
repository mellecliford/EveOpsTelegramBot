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
        "EveOps Downloader Bot\n\n"
        "Send any link → get MP4 or MP3 instantly\n"
        "Zero watermarks • All platforms supported"
    )

@dp.message(F.text.regexp(r"https?://"))
async def handle_link(message: types.Message):
    url = message.text.strip()
    await message.reply("Analyzing link...")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Video (MP4)", callback_data=f"mp4|{url}")],
        [InlineKeyboardButton(text="Audio (MP3)", callback_data=f"mp3|{url}")],
        [InlineKeyboardButton(text="Both", callback_data=f"both|{url}")]
    ])
    await message.answer("Choose format:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("mp4|") | F.data.startswith("mp3|") | F.data.startswith("both|"))
async def process_callback(callback: types.CallbackQuery):
    mode, url = callback.data.split("|", 1)
    await callback.message.edit_text("Downloading highest quality... (10–60s)")

    try:
        if "mp4" in mode or "both" in mode:
            path = await download_video(url)
            await bot.send_chat_action(callback.message.chat.id, "upload_video")
            await callback.message.answer_video(FSInputFile(path), caption="EveOps • No watermarks")
            os.remove(path)

        if "mp3" in mode or "both" in mode:
            path = await download_audio(url)
            await bot.send_chat_action(callback.message.chat.id, "upload_document")
            await callback.message.answer_audio(FSInputFile(path), caption="EveOps • 320kbps MP3")
            os.remove(path)

        await callback.message.delete()
    except Exception as e:
        error_msg = str(e).lower()
        if "private" in error_msg or "unavailable" in error_msg:
            await callback.message.edit_text("❌ Video is private/deleted. Try a public link.")
        elif "facebook" in url.lower() and "parse" in error_msg:
            await callback.message.edit_text("❌ Facebook error: Export fresh cookies.txt and redeploy.")
        else:
            await callback.message.edit_text(f"❌ {str(e)}\nTry a different link.")

async def main():
    print("EveOps Bot ONLINE!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
