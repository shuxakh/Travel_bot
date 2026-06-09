from telegram import Update
from telegram.ext import ContextTypes

FOOD_CARDS = {
    "madrid": [
        {
            "photo": "https://source.unsplash.com/1200x800/?spanish,restaurant,madrid",
            "caption": "🍽 Sobrino de Botín\n🇪🇸 Мадрид\n\n✨ Исторический ресторан с традиционной испанской кухней.\n💶 Средний чек: €35–50\n🥘 Пробовать: cochinillo, мясо, классика Мадрида\n\n📍 Карта:\nhttps://www.google.com/maps/search/?api=1&query=Sobrino+de+Botin+Madrid",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?tapas,madrid,food",
            "caption": "🍷 Mercado de San Miguel\n🇪🇸 Мадрид\n\n✨ Красивый рынок для тапас, закусок и лёгкого ужина.\n💶 Средний чек: €15–30\n🥘 Пробовать: тапас, хамон, морепродукты, крокеты\n\n📍 Карта:\nhttps://www.google.com/maps/search/?api=1&query=Mercado+San+Miguel+Madrid",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?paella,madrid,restaurant",
            "caption": "🥘 Menú del día\n🇪🇸 Мадрид\n\n✨ Практичный вариант на обед: первое + второе + напиток.\n💶 Обычно: €12–18\n✅ Хорошо, когда не хочется дорогой ресторан.\n\n📍 Поиск рядом:\nhttps://www.google.com/maps/search/?api=1&query=menu+del+dia+Madrid",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?churros,madrid",
            "caption": "☕ Churros con chocolate\n🇪🇸 Мадрид\n\n✨ Классика для сладкой паузы.\n💶 Обычно: €5–10\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=churros+con+chocolate+Madrid",
        },
    ],
    "barcelona": [
        {
            "photo": "https://source.unsplash.com/1200x800/?barcelona,tapas,food",
            "caption": "🍤 La Boqueria\n🇪🇸 Барселона\n\n✨ Рынок для быстрого обеда, фруктов, тапас и морепродуктов.\n💶 Средний чек: €15–30\n\n📍 Карта:\nhttps://www.google.com/maps/search/?api=1&query=La+Boqueria+Barcelona",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?paella,barcelona",
            "caption": "🥘 Паэлья\n🇪🇸 Барселона\n\n✨ Лучше искать места с хорошими отзывами, не на самой туристической улице.\n💶 Средний чек: €20–35\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=paella+restaurant+Barcelona",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?tapas,barcelona",
            "caption": "🍷 Тапас-бары\n🇪🇸 Барселона\n\n✨ Удобно на вечер: взять несколько маленьких блюд и попробовать разное.\n💶 Средний чек: €15–30\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=tapas+bar+Barcelona",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?seafood,barcelona",
            "caption": "🦐 Морепродукты\n🇪🇸 Барселона\n\n✨ Хороший вариант после прогулки у моря.\n💶 Средний чек: €25–45\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=seafood+restaurant+Barcelona",
        },
    ],
    "rome": [
        {
            "photo": "https://source.unsplash.com/1200x800/?carbonara,rome,pasta",
            "caption": "🍝 Карбонара / аматричана / cacio e pepe\n🇮🇹 Рим\n\n✨ Главная римская классика.\n💶 Средний чек: €18–35\n✅ Хорошо для первого ужина в Риме.\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=carbonara+restaurant+Rome",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?trastevere,rome,restaurant",
            "caption": "🍷 Трастевере\n🇮🇹 Рим\n\n✨ Атмосферный район для вечернего ужина.\n💶 Средний чек: €20–40\n✅ Лучше идти вечером, когда район оживает.\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=Trastevere+restaurants+Rome",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?pizza,rome,italy",
            "caption": "🍕 Римская пицца\n🇮🇹 Рим\n\n✨ Быстрый и недорогой вариант между прогулками.\n💶 Средний чек: €8–18\n✅ Удобно на обед, когда не хочется долго сидеть.\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=best+pizza+Rome",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?rome,market,food",
            "caption": "🥙 Mercato Centrale Roma\n🇮🇹 Рим\n\n✨ Удобный фуд-холл рядом с Termini: можно выбрать разную еду.\n💶 Средний чек: €12–25\n✅ Хорошо, если вкусы у всех разные.\n\n📍 Карта:\nhttps://www.google.com/maps/search/?api=1&query=Mercato+Centrale+Roma",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?gelato,rome",
            "caption": "🍨 Джелато\n🇮🇹 Рим\n\n✨ Сладкая пауза после прогулки.\n💶 Обычно: €3–7\n✅ Ищите gelateria с хорошим рейтингом, не только у главных туристических мест.\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=best+gelato+Rome",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?italian,restaurant,rome",
            "caption": "🍽 Траттория рядом с вашим районом\n🇮🇹 Рим\n\n✨ Самый удобный формат: простая местная кухня без пафоса.\n💶 Средний чек: €18–35\n✅ Смотрите рейтинг 4.3+ и свежие отзывы.\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=trattoria+near+Raeli+Hotel+Lux+Rome",
        },
    ],
    "milan": [
        {
            "photo": "https://source.unsplash.com/1200x800/?milan,aperitivo,food",
            "caption": "🍹 Aperitivo\n🇮🇹 Милан\n\n✨ Миланский формат: напиток + закуски вечером.\n💶 Обычно: €12–25\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=Aperitivo+Navigli+Milan",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?risotto,milan,food",
            "caption": "🍚 Risotto alla Milanese\n🇮🇹 Милан\n\n✨ Классическое миланское блюдо.\n💶 Средний чек: €20–40\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=Risotto+Ossobuco+Trattoria+Milan",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?pizza,milan",
            "caption": "🍕 Пицца в Милане\n🇮🇹 Милан\n\n✨ Хороший быстрый вариант на ужин.\n💶 Средний чек: €12–25\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=pizza+restaurant+Milan",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?eataly,milan",
            "caption": "🛒 Eataly Milano\n🇮🇹 Милан\n\n✨ Гастрономический центр: еда, продукты, несколько форматов.\n💶 Средний чек: €15–35\n\n📍 Карта:\nhttps://www.google.com/maps/search/?api=1&query=Eataly+Milano+Smeraldo",
        },
    ],
    "como": [
        {
            "photo": "https://source.unsplash.com/1200x800/?lake,como,restaurant",
            "caption": "🌊 Обед у озера\n🇮🇹 Комо\n\n✨ Лучше выбрать кафе/ресторан у набережной, но смотреть рейтинг.\n💶 Средний чек: €20–40\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=Lake+Como+restaurant+Como",
        },
        {
            "photo": "https://source.unsplash.com/1200x800/?pasta,como,italy",
            "caption": "🍝 Паста / ризотто\n🇮🇹 Комо\n\n✨ Спокойный обед после прогулки по набережной.\n💶 Средний чек: €18–35\n\n📍 Поиск:\nhttps://www.google.com/maps/search/?api=1&query=pasta+risotto+restaurant+Como",
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
    return "rome"


async def food_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    city = detect_food_city(text)
    for card in FOOD_CARDS.get(city, FOOD_CARDS["rome"]):
        try:
            await update.message.reply_photo(photo=card["photo"], caption=card["caption"])
        except Exception:
            await update.message.reply_text(card["caption"], disable_web_page_preview=True)
