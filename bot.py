@dp.callback_query(F.data.startswith("mp4|") | F.data.startswith("mp3|") | F.data.startswith("both|"))
async def process_callback(callback: types.CallbackQuery):
    mode, url = callback.data.split("|", 1)
    await callback.message.edit_text("Downloading highest quality... (10–60s)")

    try:
        if "mp4" in mode or "both" in mode:
            path = await download_video(url)
            file_size = os.path.getsize(path) / (1024 * 1024)  # MB
            await bot.send_chat_action(callback.message.chat.id, "upload_video")
            
            if file_size > 50:
                # Fallback to document (unlimited size)
                caption = "EveOps • No watermarks (sent as file due to size)"
                await callback.message.answer_document(FSInputFile(path), caption=caption)
            else:
                await callback.message.answer_video(FSInputFile(path), caption="EveOps • No watermarks")
            
            os.remove(path)

        if "mp3" in mode or "both" in mode:
            path = await download_audio(url)
            await bot.send_chat_action(callback.message.chat.id, "upload_audio")
            await callback.message.answer_audio(FSInputFile(path), caption="EveOps • 320kbps MP3")
            os.remove(path)

        await callback.message.delete()
    except Exception as e:
        error_msg = str(e).lower()
        if "private" in error_msg or "unavailable" in error_msg:
            await callback.message.edit_text("❌ Video is private/deleted. Try a public link.")
        elif "size" in error_msg or "large" in error_msg:
            await callback.message.edit_text("❌ File too large even after compression. Try a shorter video.")
        else:
            await callback.message.edit_text(f"❌ {str(e)}\nTry a different link.")
