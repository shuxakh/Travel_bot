from urllib.parse import quote_plus

from telegram import Update
from telegram.ext import ContextTypes

TOUR_PRESETS = {
    "colosseum": {
        "title": "🏛 Колизей",
        "city": "🇮🇹 Рим",
        "query": "Colosseum Rome skip the line guided tour",
        "maps": "Colosseum Rome",
        "tips": "Сравните entry ticket, guided tour и skip-the-line. Для первого раза лучше брать вариант с Форумом и Палатином.",
    },
    "vatican": {
        "title": "⛪ Ватикан + Сикстинская капелла",
        "city": "🇮🇹 Рим",
        "query": "Vatican Museums Sistine Chapel Rome tickets guided tour",
        "maps": "Vatican Museums Rome",
        "tips": "Лучше смотреть skip-the-line или guided tour. Проверяйте время входа и язык экскурсии.",
    },
    "pantheon": {
        "title": "🏛 Пантеон",
        "city": "🇮🇹 Рим",
        "query": "Pantheon Rome ticket audio guide",
        "maps": "Pantheon Rome",
        "tips": "Можно брать простой билет или аудиогид. Смотрите, включён ли конкретный time slot.",
    },
    "sagrada": {
        "title": "⛪ Sagrada Familia",
        "city": "🇪🇸 Барселона",
        "query": "Sagrada Familia Barcelona tickets guided tour towers",
        "maps": "Sagrada Familia Barcelona",
        "tips": "Сравните обычный билет, guided tour и билет с башнями. Бронировать заранее.",
    },
    "park_guell": {
        "title": "🌿 Park Güell",
        "city": "🇪🇸 Барселона",
        "query": "Park Guell Barcelona tickets guided tour",
        "maps": "Park Guell Barcelona",
        "tips": "Смотрите вход в Monumental Zone. Удобнее выбирать время утром или ближе к вечеру.",
    },
    "prado": {
        "title": "🖼 Museo del Prado",
        "city": "🇪🇸 Мадрид",
        "query": "Prado Museum Madrid tickets guided tour",
        "maps": "Museo del Prado Madrid",
        "tips": "Можно взять простой билет или тур с гидом по главным картинам, чтобы не тратить силы на весь музей.",
    },
    "royal_palace_madrid": {
        "title": "👑 Королевский дворец",
        "city": "🇪🇸 Мадрид",
        "query": "Royal Palace Madrid tickets guided tour",
        "maps": "Palacio Real Madrid",
        "tips": "Смотрите варианты с быстрым входом и гидом. Уточняйте часы, дворец иногда закрывают под мероприятия.",
    },
    "duomo_milan": {
        "title": "⛪ Duomo di Milano",
        "city": "🇮🇹 Милан",
        "query": "Duomo Milan tickets rooftop guided tour",
        "maps": "Duomo Milan",
        "tips": "Хороший вариант — билет на крышу. Уточняйте лифт или лестницы, если нужен комфортный темп.",
    },
    "lake_como": {
        "title": "🏞 Озеро Комо",
        "city": "🇮🇹 Комо",
        "query": "Lake Como day trip from Milan boat tour",
        "maps": "Lake Como Como",
        "tips": "Смотрите day trip from Milan, boat tour или самостоятельный вариант поездом + прогулка по Комо.",
    },
}

CITY_QUERIES = {
    "rome": ["colosseum", "vatican", "pantheon"],
    "barcelona": ["sagrada", "park_guell"],
    "madrid": ["prado", "royal_palace_madrid"],
    "milan": ["duomo_milan", "lake_como"],
    "como": ["lake_como"],
}


def gyg_url(query: str) -> str:
    return "https://www.getyourguide.com/s/?q=" + quote_plus(query)


def maps_url(query: str) -> str:
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(query)


def detect_tour_keys(text: str) -> list[str]:
    t = (text or "").lower()
    keys = []

    if "колиз" in t or "colosseum" in t or "coliseum" in t:
        keys.append("colosseum")
    if "ватикан" in t or "vatican" in t or "сикст" in t or "sistine" in t:
        keys.append("vatican")
    if "пантеон" in t or "pantheon" in t:
        keys.append("pantheon")
    if "саград" in t or "sagrada" in t:
        keys.append("sagrada")
    if "гуэль" in t or "guell" in t or "güell" in t:
        keys.append("park_guell")
    if "прадо" in t or "prado" in t:
        keys.append("prado")
    if "королевск" in t or "royal palace" in t or "palacio real" in t:
        keys.append("royal_palace_madrid")
    if "дуом" in t or "duomo" in t:
        keys.append("duomo_milan")
    if "комо" in t or "como" in t or "lake como" in t:
        keys.append("lake_como")

    if keys:
        return list(dict.fromkeys(keys))

    if "рим" in t or "rome" in t or "roma" in t:
        return CITY_QUERIES["rome"]
    if "барсел" in t or "barcelona" in t:
        return CITY_QUERIES["barcelona"]
    if "мадрид" in t or "madrid" in t:
        return CITY_QUERIES["madrid"]
    if "милан" in t or "milan" in t or "milano" in t:
        return CITY_QUERIES["milan"]
    if "комо" in t or "como" in t:
        return CITY_QUERIES["como"]

    return ["colosseum", "vatican", "sagrada", "lake_como"]


def make_caption(item: dict) -> str:
    return (
        f"{item['title']}\n"
        f"{item['city']}\n\n"
        f"🎟 Билеты / туры / экскурсии\n"
        f"💶 Актуальная цена: смотреть на GetYourGuide\n"
        f"💡 Совет: {item['tips']}\n\n"
        f"🔗 GetYourGuide:\n{gyg_url(item['query'])}\n\n"
        f"📍 Карта:\n{maps_url(item['maps'])}"
    )


async def tours_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    keys = detect_tour_keys(text)
    for key in keys[:6]:
        item = TOUR_PRESETS[key]
        await update.message.reply_text(make_caption(item), disable_web_page_preview=True)
