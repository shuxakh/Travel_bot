import json
import logging
from datetime import date
from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import ContextTypes
from config import OPENAI_API_KEY
from db import init_db, save_message, get_history
from prompts import SYSTEM_PROMPT
from pathlib import Path

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=OPENAI_API_KEY)
init_db()

# Загружаем базу знаний
KB_PATH = Path(__file__).parent / "knowledge_base.json"
with open(KB_PATH, encoding="utf-8") as f:
    KB = json.load(f)


def city_info(city_key: str) -> str:
    """Формирует текст с информацией о городе из базы знаний."""
    c = KB["cities"][city_key]
    hotel = next((h for h in KB["hotels"] if h["city"].lower() == city_key or
                  (city_key == "rome" and h["city"] == "Рим") or
                  (city_key == "milan" and h["city"] == "Милан") or
                  (city_key == "madrid" and h["city"] == "Мадрид") or
                  (city_key == "barcelona" and h["city"] == "Барселона")), None)

    lines = [f"📅 *{c['dates']}*"]
    if hotel:
        lines.append(f"🏨 *{hotel['name']}* — ${hotel['price_usd']} (завтрак включён)")
        lines.append(f"📍 [Отель на карте]({hotel['maps']})")

    lines.append("\n🏛 *Достопримечательности:*")
    for a in c["attractions"]:
        price = f"€{a['price_eur']}" if a.get("price_eur", 0) > 0 else "Бесплатно"
        line = f"• *{a['name']}* — {price} | {a.get('hours', '')}"
        if a.get("booking"):
            line += f"\n  ⚠️ {a['booking']}"
        if a.get("maps"):
            line += f"\n  📍 [Карта]({a['maps']})"
        lines.append(line)

    t = c["transport"]
    lines.append("\n🚇 *Транспорт:*")
    for k, v in t.items():
        if k != "tip":
            lines.append(f"• {v}")
    if t.get("tip"):
        lines.append(f"💡 {t['tip']}")

    lines.append(f"\n🍽 *Бюджет на еду:* {c['food_budget_per_day']}")
    return "\n".join(lines)


async def ask_gpt(user_id: int, user_text: str) -> str:
    """Отправляет запрос в GPT с историей и базой знаний."""
    history = get_history(user_id)
    save_message(user_id, "user", user_text)

    # Добавляем базу знаний в системный промпт
    kb_text = json.dumps(KB, ensure_ascii=False, indent=2)
    full_system = SYSTEM_PROMPT + f"\n\nБАЗА ДАННЫХ ПОЕЗДКИ (JSON):\n{kb_text}"

    messages = [{"role": "system", "content": full_system}]
    messages += history
    messages.append({"role": "user", "content": user_text})

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1000,
        temperature=0.5,
    )
    answer = response.choices[0].message.content
    save_message(user_id, "assistant", answer)
    return answer


# ─── КОМАНДЫ ────────────────────────────────────────────────────────────────

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Привет! Я ваш персональный гид по поездке.\n\n"
        "🗺 *Маршрут:*\n"
        "17–19 июн → 🇪🇸 Мадрид\n"
        "19–21 июн → 🇪🇸 Барселона\n"
        "21–24 июн → 🇮🇹 Рим\n"
        "24–26 июн → 🇮🇹 Милан\n\n"
        "📋 *Команды:*\n"
        "/madrid — Мадрид\n"
        "/barcelona — Барселона\n"
        "/rome — Рим\n"
        "/milan — Милан\n"
        "/today — Что сегодня?\n"
        "/budget — Бюджет поездки\n"
        "/transport — Транспорт\n"
        "/map — Карта текущего отеля\n"
        "/help — Помощь\n\n"
        "💬 Или просто пишите вопрос — отвечу как гид!"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def madrid(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🇪🇸 *МАДРИД*\n\n" + city_info("madrid"),
        parse_mode="Markdown", disable_web_page_preview=True
    )


async def barcelona(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🇪🇸 *БАРСЕЛОНА*\n\n" + city_info("barcelona"),
        parse_mode="Markdown", disable_web_page_preview=True
    )


async def rome(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🇮🇹 *РИМ*\n\n" + city_info("rome"),
        parse_mode="Markdown", disable_web_page_preview=True
    )


async def milan(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🇮🇹 *МИЛАН*\n\n" + city_info("milan"),
        parse_mode="Markdown", disable_web_page_preview=True
    )


async def today(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    today_date = date.today()
    schedule = {
        (2026, 6, 17): ("🇪🇸 Мадрид", "Прилёт в 16:55. Трансфер в отель ($53). Вечер — отдых, прогулка по центру.", "/madrid"),
        (2026, 6, 18): ("🇪🇸 Мадрид", "Полный день в Мадриде. Музей Прадо, парк Ретиро, площадь Майор.", "/madrid"),
        (2026, 6, 19): ("🇪🇸 Барселона", "Поезд OUIGO 09:31 с Аточа. Прибытие в Барселону 12:58.", "/barcelona"),
        (2026, 6, 20): ("🇪🇸 Барселона", "Полный день. Саграда Фамилия, парк Гуэль, Готический квартал.", "/barcelona"),
        (2026, 6, 21): ("🇮🇹 Рим", "Вылет Vueling 08:00 из BCN. Прилёт в Рим 09:50. Заселение, вечером — Фонтан Треви.", "/rome"),
        (2026, 6, 22): ("🇮🇹 Рим", "Колизей + Форум + Палатин. Вечер в Трастевере.", "/rome"),
        (2026, 6, 23): ("🇮🇹 Рим", "Ватикан + Сикстинская капелла. Пантеон.", "/rome"),
        (2026, 6, 24): ("🇮🇹 Милан", "Поезд Italo 10:05 из Roma Termini. Прибытие в Милан 13:15.", "/milan"),
        (2026, 6, 25): ("🇮🇹 Милан", "Полный день. Дуомо, Галерея Виттори, замок Сфорца, район Навильи вечером.", "/milan"),
        (2026, 6, 26): ("✈️ Домой", "Вылет HY-256 в 20:50 из Мальпенсы. Выезжать не позже 17:30.\nПоезд Malpensa Express €13 от Milano Centrale.", "/milan"),
    }
    key = (today_date.year, today_date.month, today_date.day)
    if key in schedule:
        city, desc, cmd = schedule[key]
        await update.message.reply_text(
            f"📅 *Сегодня {today_date.strftime('%d.%m.%Y')}*\n\n"
            f"{city}\n{desc}\n\nПодробнее: {cmd}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"📅 *{today_date.strftime('%d.%m.%Y')}*\n\nЭта дата не входит в маршрут поездки (17–26 июня 2026).",
            parse_mode="Markdown"
        )


async def budget(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    b = KB["total_budget"]
    text = (
        "💰 *БЮДЖЕТ ПОЕЗДКИ*\n\n"
        f"🏨 Отели: ${b['hotels_usd']:,}\n"
        f"✈️ Перелёты и поезда: ~${b['flights_estimated_usd']:,}\n"
        f"🚖 Трансфер Мадрид: ${b['transfer_madrid_usd']}\n"
        f"🍽 Питание (9 дней): ~€{b['food_9_days_eur']:,}\n"
        f"🏛 Музеи и аттракции: ~€{b['attractions_eur']}\n"
        f"🚇 Городской транспорт: ~€{b['transport_local_eur']}\n\n"
        f"📊 *ИТОГО: ~${b['total_estimated_usd']:,}*\n\n"
        "_Завтраки включены в стоимость отелей._"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def transport(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    today_date = date.today()
    if date(2026, 6, 17) <= today_date <= date(2026, 6, 18):
        city_key = "madrid"
    elif date(2026, 6, 19) <= today_date <= date(2026, 6, 20):
        city_key = "barcelona"
    elif date(2026, 6, 21) <= today_date <= date(2026, 6, 23):
        city_key = "rome"
    else:
        city_key = "milan"

    c = KB["cities"][city_key]
    t = c["transport"]
    lines = [f"🚇 *Транспорт — {city_key.upper()}*\n"]
    for k, v in t.items():
        if k == "tip":
            lines.append(f"\n💡 {v}")
        else:
            lines.append(f"• {v}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def map_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    today_date = date.today()
    if date(2026, 6, 17) <= today_date <= date(2026, 6, 18):
        hotel = next(h for h in KB["hotels"] if h["city"] == "Мадрид")
    elif date(2026, 6, 19) <= today_date <= date(2026, 6, 20):
        hotel = next(h for h in KB["hotels"] if h["city"] == "Барселона")
    elif date(2026, 6, 21) <= today_date <= date(2026, 6, 23):
        hotel = next(h for h in KB["hotels"] if h["city"] == "Рим")
    else:
        hotel = next(h for h in KB["hotels"] if h["city"] == "Милан")

    await update.message.reply_text(
        f"🏨 *{hotel['name']}*\n📅 {hotel['dates']}\n\n📍 [Открыть на карте]({hotel['maps']})",
        parse_mode="Markdown"
    )


async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 *Что я умею:*\n\n"
        "/start — Главное меню\n"
        "/madrid — Всё о Мадриде\n"
        "/barcelona — Всё о Барселоне\n"
        "/rome — Всё о Риме\n"
        "/milan — Всё о Милане\n"
        "/today — Программа на сегодня\n"
        "/budget — Бюджет поездки\n"
        "/transport — Транспорт в текущем городе\n"
        "/map — Карта текущего отеля\n\n"
        "💬 *Или просто напишите вопрос:*\n"
        "«Как доехать до Колизея?»\n"
        "«Где поужинать в Барселоне?»\n"
        "«Сколько стоит такси до аэропорта?»\n"
        "«Что посмотреть завтра?»"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def chat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Свободный чат через GPT."""
    user_id = update.effective_user.id
    user_text = update.message.text

    await update.message.chat.send_action("typing")
    try:
        answer = await ask_gpt(user_id, user_text)
        await update.message.reply_text(answer, parse_mode="Markdown",
                                        disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"GPT error: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте ещё раз.")
