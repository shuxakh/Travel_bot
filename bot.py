import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN
from handlers import (
    start, madrid, barcelona, rome, milan,
    today, budget, transport, map_cmd, help_cmd, chat, photo_chat
)
from api_handlers import weather_cmd, currency_cmd, apis_cmd, flight_cmd
from plan_handlers import plan_cmd, cards_cmd
from food_handlers import food_cmd

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

FULL_PLAN_FILTER = filters.TEXT & ~filters.COMMAND & filters.Regex(
    r"(?i)(полный\s+план|план\s+поездки|весь\s+план|весь\s+маршрут|маршрут\s+поездки|полностью\s+план|все\s+дни|покажи\s+план)"
)

FOOD_FILTER = filters.TEXT & ~filters.COMMAND & filters.Regex(
    r"(?i)(где\s+поесть|что\s+поесть|куда\s+пойти\s+поесть|ресторан|рестораны|еда|кафе|ужин|обед|завтрак|тапас|паста|паэлья|аперитив)"
)

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("plan", plan_cmd))
    app.add_handler(CommandHandler("cards", cards_cmd))
    app.add_handler(CommandHandler("food", food_cmd))
    app.add_handler(CommandHandler("madrid", madrid))
    app.add_handler(CommandHandler("barcelona", barcelona))
    app.add_handler(CommandHandler("rome", rome))
    app.add_handler(CommandHandler("milan", milan))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("budget", budget))
    app.add_handler(CommandHandler("transport", transport))
    app.add_handler(CommandHandler("map", map_cmd))
    app.add_handler(CommandHandler("weather", weather_cmd))
    app.add_handler(CommandHandler("currency", currency_cmd))
    app.add_handler(CommandHandler("flight", flight_cmd))
    app.add_handler(CommandHandler("apis", apis_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.PHOTO, photo_chat))
    app.add_handler(MessageHandler(FULL_PLAN_FILTER, cards_cmd))
    app.add_handler(MessageHandler(FOOD_FILTER, food_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    logging.info("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
