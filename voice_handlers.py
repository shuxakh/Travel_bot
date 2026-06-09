import logging
import tempfile
from pathlib import Path

from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import ContextTypes

from config import OPENAI_API_KEY
from handlers import ask_gpt

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def voice_chat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Понимает голосовые сообщения Telegram и отвечает текстом."""
    user_id = update.effective_user.id

    await update.message.chat.send_action("typing")
    temp_path = None

    try:
        voice = update.message.voice
        if not voice:
            await update.message.reply_text("Отправьте именно голосовое сообщение.")
            return

        tg_file = await voice.get_file()
        voice_data = await tg_file.download_as_bytearray()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
            tmp.write(bytes(voice_data))
            temp_path = tmp.name

        with open(temp_path, "rb") as audio_file:
            transcription = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ru",
            )

        text = (transcription.text or "").strip()
        if not text:
            await update.message.reply_text("Не получилось разобрать голос. Попробуйте сказать чуть чётче.")
            return

        await update.message.reply_text(f"🎙 Я понял:\n{text}")

        answer = await ask_gpt(user_id, text)
        await update.message.reply_text(answer, disable_web_page_preview=True)

    except Exception as e:
        logger.exception(f"Voice message error: {e}")
        await update.message.reply_text("Не получилось разобрать голосовое сообщение. Попробуйте ещё раз.")

    finally:
        if temp_path:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except Exception:
                pass
