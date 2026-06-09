from datetime import datetime, timezone
from urllib.parse import quote_plus
import os
import re
import httpx

CITY_COORDS = {
    "madrid": {"name_ru": "Мадрид", "lat": 40.4168, "lon": -3.7038, "timezone": "Europe/Madrid"},
    "barcelona": {"name_ru": "Барселона", "lat": 41.3874, "lon": 2.1686, "timezone": "Europe/Madrid"},
    "rome": {"name_ru": "Рим", "lat": 41.9028, "lon": 12.4964, "timezone": "Europe/Rome"},
    "milan": {"name_ru": "Милан", "lat": 45.4642, "lon": 9.1900, "timezone": "Europe/Rome"},
    "como": {"name_ru": "Комо", "lat": 45.8081, "lon": 9.0852, "timezone": "Europe/Rome"},
}

WEATHER_CODES_RU = {
    0: "ясно", 1: "в основном ясно", 2: "переменная облачность", 3: "пасмурно",
    45: "туман", 48: "туман", 51: "слабая морось", 53: "морось", 55: "сильная морось",
    61: "слабый дождь", 63: "дождь", 65: "сильный дождь", 80: "кратковременный дождь",
    81: "ливни", 82: "сильные ливни", 95: "гроза", 96: "гроза с градом", 99: "сильная гроза",
}


def detect_city(text: str, default: str = "milan") -> str:
    t = (text or "").lower()
    if "мадрид" in t or "madrid" in t: return "madrid"
    if "барсел" in t or "barcelona" in t: return "barcelona"
    if "рим" in t or "rome" in t or "roma" in t: return "rome"
    if "комо" in t or "como" in t: return "como"
    if "милан" in t or "milan" in t or "milano" in t: return "milan"
    return default


def current_trip_city() -> str:
    today = datetime.now(timezone.utc).date()
    if today in [datetime(2026, 6, 17).date(), datetime(2026, 6, 18).date()]: return "madrid"
    if today in [datetime(2026, 6, 19).date(), datetime(2026, 6, 20).date()]: return "barcelona"
    if datetime(2026, 6, 21).date() <= today <= datetime(2026, 6, 23).date(): return "rome"
    if today == datetime(2026, 6, 25).date(): return "como"
    return "milan"


def maps_search(query: str) -> str:
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(query)


async def get_weather(city_key: str) -> str:
    city = CITY_COORDS.get(city_key, CITY_COORDS["milan"])
    api_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": city["lat"], "longitude": city["lon"],
        "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,uv_index_max",
        "forecast_days": 1, "timezone": city["timezone"],
    }
    async with httpx.AsyncClient(timeout=12) as http:
        response = await http.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()

    cur = data.get("current", {})
    daily = data.get("daily", {})
    temp = cur.get("temperature_2m")
    feels = cur.get("apparent_temperature")
    wind = cur.get("wind_speed_10m")
    desc = WEATHER_CODES_RU.get(cur.get("weather_code"), "погода уточняется")
    tmax = (daily.get("temperature_2m_max") or [None])[0]
    tmin = (daily.get("temperature_2m_min") or [None])[0]
    rain = (daily.get("precipitation_probability_max") or [None])[0]
    uv = (daily.get("uv_index_max") or [None])[0]

    advice = []
    if temp is not None and temp >= 27: advice.append("возьмите воду и кепку")
    if rain is not None and rain >= 40: advice.append("лучше взять зонт")
    if uv is not None and uv >= 6: advice.append("нужен SPF")
    if not advice: advice.append("погода нормальная для прогулки")

    return (
        f"🌤 Погода — {city['name_ru']}\n"
        f"Сейчас: {temp}°C, ощущается как {feels}°C, {desc}.\n"
        f"Сегодня: от {tmin}°C до {tmax}°C. Осадки: {rain}%. UV: {uv}. Ветер: {wind} км/ч.\n"
        f"Совет: {', '.join(advice)}."
    )


async def convert_currency(amount: float, from_currency: str = "EUR", to_currency: str = "USD") -> str:
    api_url = "https://api.frankfurter.app/latest"
    params = {"amount": amount, "from": from_currency.upper(), "to": to_currency.upper()}
    async with httpx.AsyncClient(timeout=12) as http:
        response = await http.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
    result = data.get("rates", {}).get(to_currency.upper())
    if result is None:
        return "Не получилось получить курс. Попробуйте позже."
    return f"💱 {amount:g} {from_currency.upper()} ≈ {result:.2f} {to_currency.upper()}\nКурс Frankfurter на дату: {data.get('date', 'сегодня')}"


async def flight_status(flight_number: str) -> str:
    api_key = os.getenv("AVIATIONSTACK_API_KEY", "")
    if not api_key:
        return "✈️ AviationStack не подключён. Добавьте AVIATIONSTACK_API_KEY в Render Environment."
    flight_number = (flight_number or "").upper().replace("-", "").strip()
    if not flight_number:
        return "Напишите номер рейса. Пример: /flight VY6106"
    async with httpx.AsyncClient(timeout=15) as http:
        response = await http.get(
            "http://api.aviationstack.com/v1/flights",
            params={"access_key": api_key, "flight_iata": flight_number},
        )
        response.raise_for_status()
        data = response.json()
    flights = data.get("data") or []
    if not flights:
        return f"✈️ По рейсу {flight_number} данных не нашёл. Проверьте номер или дату рейса."
    f = flights[0]
    dep = f.get("departure") or {}
    arr = f.get("arrival") or {}
    airline = f.get("airline") or {}
    status = f.get("flight_status") or "неизвестно"
    return (
        f"✈️ Рейс {flight_number}\n"
        f"Авиакомпания: {airline.get('name') or '—'}\n"
        f"Статус: {status}\n\n"
        f"Вылет: {dep.get('airport') or '—'}\n"
        f"Терминал: {dep.get('terminal') or '—'}, гейт: {dep.get('gate') or '—'}\n"
        f"Плановое время: {dep.get('scheduled') or '—'}\n"
        f"Фактическое/оценочное: {dep.get('actual') or dep.get('estimated') or '—'}\n\n"
        f"Прилёт: {arr.get('airport') or '—'}\n"
        f"Терминал: {arr.get('terminal') or '—'}, гейт: {arr.get('gate') or '—'}\n"
        f"Плановое время: {arr.get('scheduled') or '—'}\n"
        f"Фактическое/оценочное: {arr.get('actual') or arr.get('estimated') or '—'}"
    )


def extract_amount(text: str) -> float | None:
    match = re.search(r"(\d+(?:[\.,]\d+)?)", text or "")
    return float(match.group(1).replace(",", ".")) if match else None


def extract_flight_number(text: str) -> str | None:
    match = re.search(r"\b([A-ZА-Я]{2}\s*-?\s*\d{2,5})\b", (text or "").upper())
    if not match:
        return None
    return match.group(1).replace(" ", "").replace("-", "")


def api_status() -> str:
    aviation = "✅ Статусы рейсов AviationStack — подключён" if os.getenv("AVIATIONSTACK_API_KEY") else "⚠️ Статусы рейсов — нужен AVIATIONSTACK_API_KEY"
    return (
        "🔌 API-статус Travel Bot\n\n"
        "✅ Погода Open-Meteo — работает без ключа\n"
        "✅ Валюта Frankfurter — работает без ключа\n"
        f"{aviation}\n"
        "⚠️ События/концерты — добавим через Ticketmaster API key\n"
        "ℹ️ Транспорт — пока через Google Maps links"
    )
