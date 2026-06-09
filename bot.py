import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN
from handlers import (
    start, madrid, barcelona, rome, milan,
    today, budget, transport, map_cmd, help_cmd, chat, photo_chat
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("madrid", madrid))
    app.add_handler(CommandHandler("barcelona", barcelona))
    app.add_handler(CommandHandler("rome", rome))
    app.add_handler(CommandHandler("milan", milan))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("budget", budget))
    app.add_handler(CommandHandler("transport", transport))
    app.add_handler(CommandHandler("map", map_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.PHOTO, photo_chat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    logging.info("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
