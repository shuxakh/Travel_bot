import logging
from telegram import Update
from telegram.ext import ContextTypes
from external_apis import (
    get_weather, convert_currency, extract_amount, detect_city,
    current_trip_city, api_status, flight_status, extract_flight_number
)

logger = logging.getLogger(__name__)

async def weather_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    city_key = detect_city(text, current_trip_city())
    try:
        await update.message.reply_text(await get_weather(city_key))
    except Exception as e:
        logger.exception(f"Weather API error: {e}")
        await update.message.reply_text("Не получилось получить погоду. Попробуйте позже.")

async def currency_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    amount = extract_amount(text) or 1
    try:
        await update.message.reply_text(await convert_currency(amount, "EUR", "USD"))
    except Exception as e:
        logger.exception(f"Currency API error: {e}")
        await update.message.reply_text("Не получилось получить курс. Попробуйте позже.")

async def flight_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    flight_number = extract_flight_number(text)
    if not flight_number and ctx.args:
        flight_number = "".join(ctx.args).upper().replace("-", "")
    if not flight_number:
        await update.message.reply_text("Напишите номер рейса. Пример: /flight VY6106")
        return
    try:
        await update.message.reply_text(await flight_status(flight_number))
    except Exception as e:
        logger.exception(f"Flight API error: {e}")
        await update.message.reply_text("Не получилось получить статус рейса. Проверьте номер или попробуйте позже.")

async def apis_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(api_status())
