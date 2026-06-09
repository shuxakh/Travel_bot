import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN
from handlers import (
    start, madrid, barcelona, rome, milan,
    today, budget, transport, map_cmd, help_cmd, chat, photo_chat
)
from api_handlers import weather_cmd, currency_cmd, apis_cmd, flight_cmd
from plan_handlers import plan_cmd, cards_cmd
from food_handlers import food_cmd
from tours_handlers import tours_cmd

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

FULL_PLAN_FILTER = filters.TEXT & ~filters.COMMAND & filters.Regex(
    r"(?i)(полный\s+план|план\s+поездки|весь\s+план|весь\s+маршрут|маршрут\s+поездки|полностью\s+план|все\s+дни|покажи\s+план)"
)

FOOD_FILTER = filters.TEXT & ~filters.COMMAND & filters.Regex(
    r"(?i)(где\s+поесть|что\s+поесть|куда\s+пойти\s+поесть|где\s+покушать|что\s+покушать|покушать|поесть|еда|ресторан|рестораны|кафе|ужин|обед|завтрак|тапас|паста|паэлья|аперитив|еще\s+мест|ещё\s+мест|еще\s+вариант|ещё\s+вариант|только\s+два\s+места)"
)

TOURS_FILTER = filters.TEXT & ~filters.COMMAND & filters.Regex(
    r"(?i)(getyourguide|экскурс|тур|туры|билет|билеты|skip\s*the\s*line|гид|купить\s+билет|колиз|ватикан|саград|гуэль|прадо|дуомо|пантеон)"
)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Travel bot is running")

    def log_message(self, format, *args):
        return


def start_health_server():
    port = int(os.environ.get("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logging.info(f"Health server started on port {port}")


def main():
    start_health_server()
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("plan", plan_cmd))
    app.add_handler(CommandHandler("cards", cards_cmd))
    app.add_handler(CommandHandler("food", food_cmd))
    app.add_handler(CommandHandler("tours", tours_cmd))
    app.add_handler(CommandHandler("gyg", tours_cmd))
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
    app.add_handler(MessageHandler(TOURS_FILTER, tours_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    logging.info("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
