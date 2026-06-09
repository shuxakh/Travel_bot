import logging
import re
import tempfile
from pathlib import Path

from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import ContextTypes

from config import OPENAI_API_KEY
from handlers import ask_gpt
from external_apis import (
    get_weather, get_trip_weather, detect_city_for_weather,
    current_trip_city, is_trip_weather_question
)

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=OPENAI_API_KEY, timeout=45)

WEATHER_VOICE_RE = re.compile(
    r"(погода|прогноз|температур|жарко|холодно|дожд|ветер|зонт|weather|forecast|rain|temperature)",
    re.IGNORECASE,
)


async def voice_chat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Понимает голосовые сообщения Telegram и отвечает текстом."""
    user_id = update.effective_user.id
    temp_path = None

    try:
        voice = update.message.voice
        if not voice:
            await update.message.reply_text("Отправьте именно голосовое сообщение.")
            return

        duration = voice.duration or 0
        if duration > 60:
            await update.message.reply_text("🎙 Голосовое слишком длинное. Пока лучше отправлять до 60 секунд.")
            return

        await update.message.chat.send_action("typing")
        await update.message.reply_text("🎙 Голосовое получил. Сейчас распознаю...")
        logger.info(f"Voice received: duration={duration}, file_id={voice.file_id}")

        tg_file = await voice.get_file()
        voice_data = await tg_file.download_as_bytearray()
        logger.info(f"Voice downloaded: {len(voice_data)} bytes")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
            tmp.write(bytes(voice_data))
            temp_path = tmp.name

        # Telegram voice приходит в OGG/OPUS. OpenAI Whisper нормально принимает .ogg.
        with open(temp_path, "rb") as audio_file:
            transcription = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                language="ru",
            )

        text = str(transcription or "").strip()
        logger.info(f"Voice transcribed: {text[:120]}")

        if not text:
            await update.message.reply_text("Не получилось разобрать голос. Попробуйте сказать чуть чётче.")
            return

        await update.message.reply_text(f"🎙 Я понял:\n{text}")

        if WEATHER_VOICE_RE.search(text):
            city_key = detect_city_for_weather(text, current_trip_city())
            if is_trip_weather_question(text):
                answer = await get_trip_weather(city_key)
            else:
                answer = await get_weather(city_key)
        else:
            answer = await ask_gpt(user_id, text)

        await update.message.reply_text(answer, disable_web_page_preview=True)

    except Exception as e:
        logger.exception(f"Voice message error: {type(e).__name__}: {e}")
        await update.message.reply_text(
            "Не получилось разобрать голосовое. Проверьте, что OPENAI_API_KEY работает, и попробуйте короткое голосовое до 20 секунд."
        )

    finally:
        if temp_path:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except Exception:
                pass
