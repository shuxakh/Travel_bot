from telegram import Update
from telegram.ext import ContextTypes

FOOD_CARDS = {
    "madrid": [
        {
            "photo": "https://source.unsplash.com/1200x800/?spanish,restaurant,madrid",
            "caption": "🍽 Sobrino de Botín\n🇪🇸 Мадрид\n\n✨ Атмосферный исторический ресторан, традиционная испанская кухня.\n💶 Средний чек: примерно €35–50 на человека\n🥘 Что пробовать: cochinillo, мясо, классические испанские блюда\n\n📍 Карта:\nhttps://www.google.com/maps/search/?api=1&query=Sobrino+de+Botin+Madrid",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?tapas,madrid,food",
            "caption": "🍷 Mercado de San Miguel\n🇪🇸 Мадрид\n\n✨ Красивый рынок для тапас, закусок и лёгкого ужина.\n💶 Средний чек: примерно €15–30 на человека\n🥘 Что пробовать: тапас, хамон, морепродукты, крокеты\n\n📍 Карта:\nhttps://www.google.com/maps/search/?api=1&query=Mercado+San+Miguel+Madrid",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?paella,madrid,restaurant",
            "caption": "🥘 Menú del día\n🇪🇸 Мадрид\n\n✨ Самый практичный вариант на обед: первое + второе + напиток.\n💶 Обычно: €12–18 на человека\n✅ Хорошо, когда не хочется дорогой ресторан.\n\n📍 Поиск рядом:\nhttps://www.google.com/maps/search/?api=1&query=menu+del+dia+Madrid",
        },
    ],
    "barcelona": [
        {
            "photo": "https://source.unsplash.com/1200x800/?barcelona,tapas,food",
            "caption": "🍤 La Boqueria\n🇪🇸 Барселона\n\n✨ Рынок для быстрого обеда, фруктов, тапас и морепродуктов.\n💶 Средний чек: €15–30\n\n📍 Карта:\nhttps://www.google.com/maps/search/?api=1&query=La+Boqueria+Barcelona",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?paella,barcelona",
            "caption": "🥘 Паэлья в Барселоне\n🇪🇸 Барселона\n\n✨ Лучше искать места с нормальными отзывами, не прямо на самой туристической улице.\n💶 Средний чек: €20–35\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=paella+restaurant+Barcelona",
        },
    ],
    "rome": [
        {
            "photo": "https://source.unsplash.com/1200x800/?carbonara,rome,pasta",
            "caption": "🍝 Паста в Риме\n🇮🇹 Рим\n\n✨ Карбонара, аматричана, cacio e pepe — must try.\n💶 Средний чек: €18–35\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=carbonara+restaurant+Rome",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?trastevere,rome,restaurant",
            "caption": "🍷 Трастевере\n🇮🇹 Рим\n\n✨ Атмосферный район для ужина вечером.\n💶 Средний чек: €20–40\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=Trastevere+restaurants+Rome",
        },
    ],
    "milan": [
        {
            "photo": "https://source.unsplash.com/1200x800/?milan,aperitivo,food",
            "caption": "🍹 Aperitivo\n🇮🇹 Милан\n\n✨ Миланский формат: напиток + закуски вечером.\n💶 Обычно: €12–25\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=Aperitivo+Navigli+Milan",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?risotto,milan,food",
            "caption": "🍚 Risotto alla Milanese\n🇮🇹 Милан\n\n✨ Классическое миланское блюдо. Можно взять в траттории.\n💶 Средний чек: €20–40\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=Risotto+Ossobuco+Trattoria+Milan",
        },
    ],
    "como": [
        {
            "photo": "https://source.unsplash.com/1200x800/?lake,como,restaurant",
            "caption": "🌊 Обед у озера\n🇮🇹 Комо\n\n✨ Лучше выбрать кафе/ресторан у набережной, но смотреть рейтинг.\n💶 Средний чек: €20–40\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=Lake+Como+restaurant+Como",
        },
    ],
}


def detect_food_city(text: str) -> str:
    t = (text or "").lower()
    if "мадрид" in t or "madrid" in t: return "madrid"
    if "барсел" in t or "barcelona" in t: return "barcelona"
    if "рим" in t or "rome" in t or "roma" in t: return "rome"
    if "комо" in t or "como" in t: return "como"
    if "милан" in t or "milan" in t or "milano" in t: return "milan"
    return "madrid"


async def food_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    city = detect_food_city(text)
    await update.message.reply_text("🍽 Отправляю варианты еды карточками — так удобнее смотреть, чем сухим списком.")
    for card in FOOD_CARDS.get(city, FOOD_CARDS["madrid"]):
        try:
            await update.message.reply_photo(photo=card["photo"], caption=card["caption"])
        except Exception:
            await update.message.reply_text(card["caption"], disable_web_page_preview=True)
