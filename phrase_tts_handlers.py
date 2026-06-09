import io
import logging
import os
import re

import httpx
from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import ContextTypes

from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY, timeout=45)

SPANISH_PHRASE_RE = re.compile(
    r"(?i)(скажи\s+как\s+будет\s+на\s+испанск|как\s+сказать\s+по[-\s]?испанск|переведи\s+на\s+испанск|по[-\s]?испански)"
)


def is_spanish_phrase_request(text: str) -> bool:
    return bool(SPANISH_PHRASE_RE.search(text or ""))


def extract_phrase(text: str) -> str:
    text = (text or "").strip()
    patterns = [
        r"(?i).*?скажи\s+как\s+будет\s+на\s+испанск(?:ом|ий|и)?\s*[:\-—]?\s*(.+)",
        r"(?i).*?как\s+сказать\s+по[-\s]?испанск(?:и)?\s*[:\-—]?\s*(.+)",
        r"(?i).*?переведи\s+на\s+испанск(?:ий|ом)?\s*[:\-—]?\s*(.+)",
    ]
    for pattern in patterns:
        match = re.match(pattern, text)
        if match:
            phrase = match.group(1).strip()
            return phrase.strip(' "«»')
    return text.strip(' "«»')


async def translate_to_spanish(phrase: str) -> str:
    prompt = (
        "Переведи фразу на естественный разговорный испанский для туриста. "
        "Верни только испанскую фразу без объяснений и без кавычек.\n\n"
        f"Фраза: {phrase}"
    )
    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=120,
    )
    return (response.choices[0].message.content or "").strip().strip('"«»')


async def elevenlabs_tts_mp3(text: str) -> bytes:
    api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY is not set")

    # Можно заменить через Fly secret ELEVENLABS_VOICE_ID. Этот voice_id — стандартный голос ElevenLabs.
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL").strip()
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "accept": "audio/mpeg",
        "content-type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.8,
            "style": 0.2,
            "use_speaker_boost": True,
        },
    }

    async with httpx.AsyncClient(timeout=45) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.content


async def spanish_phrase_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    phrase = extract_phrase(text)

    if not phrase or len(phrase) < 2:
        await update.message.reply_text(
            "Напишите фразу. Пример:\n"
            "Скажи как будет на испанском: где здесь поблизости туалет?"
        )
        return

    try:
        await update.message.chat.send_action("typing")
        spanish = await translate_to_spanish(phrase)

        await update.message.reply_text(
            f"🇪🇸 По-испански:\n{spanish}\n\n"
            f"🇷🇺 Смысл:\n{phrase}"
        )

        await update.message.chat.send_action("upload_voice")
        audio_bytes = await elevenlabs_tts_mp3(spanish)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "spanish_phrase.mp3"
        await update.message.reply_audio(
            audio=audio_file,
            title="Spanish phrase",
            performer="Travel Bot",
            caption="🔊 Произношение на испанском",
        )

    except Exception as e:
        logger.exception(f"Spanish phrase TTS error: {type(e).__name__}: {e}")
        await update.message.reply_text(
            "Не получилось озвучить фразу. Проверьте ELEVENLABS_API_KEY или попробуйте ещё раз."
        )
