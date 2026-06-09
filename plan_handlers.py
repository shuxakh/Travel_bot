from telegram import Update
from telegram.ext import ContextTypes

PLAN_PARTS = [
"""🧭 ПЛАН ПОЕЗДКИ 17–26 ИЮНЯ 2026

Формат: без лишнего текста, по дням, с главным маршрутом.

🇪🇸 МАДРИД

17 июня — прилёт и лёгкий вечер
16:55 — прилёт в Мадрид
Отель: Hostal Abadía Madrid
Карта: https://www.google.com/maps/search/?api=1&query=Hostal+Abadia+Madrid
Вечер: рынок Сан-Мигель, лёгкая прогулка без перегруза
Карта: https://www.google.com/maps/search/?api=1&query=Mercado+San+Miguel+Madrid

18 июня — центр Мадрида
1) Королевский дворец
https://www.google.com/maps/search/?api=1&query=Palacio+Real+Madrid
2) Пуэрта-дель-Соль
https://www.google.com/maps/search/?api=1&query=Puerta+del+Sol+Madrid
3) Площадь Майор + обед
https://www.google.com/maps/search/?api=1&query=Plaza+Mayor+Madrid
4) Музей Прадо
https://www.google.com/maps/search/?api=1&query=Museo+del+Prado+Madrid
5) Вечером — Гран-Виа или Храм Дебод
https://www.google.com/maps/search/?api=1&query=Templo+de+Debod+Madrid

19 июня — переезд в Барселону
09:31–12:58 — поезд Мадрид Аточа → Барселона Сантс""",

"""🇪🇸 БАРСЕЛОНА

19 июня — заселение и вечерний центр
Отель: Sercotel Caspe
https://www.google.com/maps/search/?api=1&query=Sercotel+Caspe+Barcelona
Вечер: Готический квартал
https://www.google.com/maps/search/?api=1&query=Barri+Gotic+Barcelona
Еда: рынок Бокерия
https://www.google.com/maps/search/?api=1&query=La+Boqueria+Barcelona

20 июня — Гауди + Монжуик
1) Саграда Фамилия — бронировать заранее
https://www.google.com/maps/search/?api=1&query=Sagrada+Familia+Barcelona
2) Парк Гуэль — лучше такси к верхнему входу, чтобы не утомить отца
https://www.google.com/maps/search/?api=1&query=Park+Guell+Barcelona
3) Дом Батльо
https://www.google.com/maps/search/?api=1&query=Casa+Batllo+Barcelona
4) Вечером Монжуик
https://www.google.com/maps/search/?api=1&query=Montjuic+Barcelona

21 июня — перелёт в Рим
08:00–09:50 — Vueling BCN → FCO""",

"""🇮🇹 РИМ

21 июня — прилёт и лёгкий вечер
Отель: Raeli Hotel Lux
https://www.google.com/maps/search/?api=1&query=Raeli+Hotel+Lux+Rome
Вечер: Фонтан Треви
https://www.google.com/maps/search/?api=1&query=Trevi+Fountain+Rome
Ужин: Трастевере
https://www.google.com/maps/search/?api=1&query=Trastevere+restaurants+Rome

22 июня — античный Рим
1) Колизей + Форум + Палатин — бронировать заранее
https://www.google.com/maps/search/?api=1&query=Colosseum+Rome
2) Площадь Навона
https://www.google.com/maps/search/?api=1&query=Piazza+Navona+Rome
3) Пантеон
https://www.google.com/maps/search/?api=1&query=Pantheon+Rome

23 июня — Ватикан
1) Музеи Ватикана + Сикстинская капелла — бронировать заранее
https://www.google.com/maps/search/?api=1&query=Vatican+Museums+Rome
2) Площадь Святого Петра
https://www.google.com/maps/search/?api=1&query=St+Peter%27s+Square+Vatican
3) Вечером Испанская лестница
https://www.google.com/maps/search/?api=1&query=Spanish+Steps+Rome

24 июня — поезд в Милан
10:05–13:15 — Roma Termini → Milano Centrale""",

"""🇮🇹 МИЛАН + КОМО

24 июня — Милан без перегруза
Отель: Brunelleschi
https://www.google.com/maps/search/?api=1&query=Hotel+Brunelleschi+Milan
После заселения:
1) Дуомо снаружи
https://www.google.com/maps/search/?api=1&query=Duomo+Milan
2) Галерея Витторио Эммануэле II
https://www.google.com/maps/search/?api=1&query=Galleria+Vittorio+Emanuele+II+Milan
3) Ужин / аперитив
https://www.google.com/maps/search/?api=1&query=Aperitivo+Navigli+Milan

25 июня — озеро Комо
Маршрут: Milano Centrale → Como S. Giovanni
https://www.google.com/maps/dir/?api=1&origin=Milano+Centrale&destination=Como+S.+Giovanni
План дня:
1) Прогулка по набережной Комо
https://www.google.com/maps/search/?api=1&query=Lake+Como+Como
2) Центр города Комо
https://www.google.com/maps/search/?api=1&query=Como+Italy
3) По желанию: фуникулёр Como → Brunate
https://www.google.com/maps/search/?api=1&query=Funicolare+Como+Brunate
Совет: если отец устанет или будет жара — оставить только набережную, кафе и короткую прогулку.

26 июня — вылет домой
Утро: спокойная прогулка/сборы
17:30 — выехать в Мальпенсу
20:50 — рейс HY-256 Милан → Ташкент"""
]

async def plan_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    for part in PLAN_PARTS:
        await update.message.reply_text(part, disable_web_page_preview=True)
