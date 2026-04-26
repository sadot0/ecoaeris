"""
EcoAeris Telegram Bot
Бот для мониторинга качества воздуха и аренды очистителей.
Каталог и тарифы синхронизированы с сайтом.
Powered by aiogram 3.x + FSM
"""

import asyncio
import logging
import sys

import aiohttp
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardButton, InlineKeyboardMarkup,
    WebAppInfo,
)
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ═══════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════
BOT_TOKEN = "8212922655:AAGmK8b9N9gmZ7MI5AfLiGTUQ30TXo-dtDs"
WAQI_TOKEN = "demo"
WEBSITE = "https://sadot0.github.io/ecoaeris"

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
log = logging.getLogger(__name__)

# ═══════════════════════════════════════════
#  ДАННЫЕ (синхронизированы с сайтом)
# ═══════════════════════════════════════════

# Каталог — те же модели что на сайте (calculator.js / shop.js)
CATALOG = {
    "budget": {
        "title": "💰 Бюджетные (до 3 млн)",
        "models": [
            {"id": "x3c", "name": "Xiaomi Mi Air Purifier 3C", "price": "1 700 000", "price_num": 1700000, "area": "45 м²", "filter": "HEPA H13", "desc": "Бесшумный ночной режим. Приложение Mi Home. Самый бюджетный вариант для квартиры."},
            {"id": "x4l", "name": "Xiaomi Mi 4 Lite", "price": "2 100 000", "price_num": 2100000, "area": "43 м²", "filter": "HEPA H13", "desc": "Компактный размер. HEPA H13 фильтр. Управление через Mi Home."},
            {"id": "x4p", "name": "Xiaomi Mi Smart 4 Pro", "price": "2 990 000", "price_num": 2990000, "area": "60 м²", "filter": "HEPA H13 + Carbon", "desc": "OLED-дисплей. CADR 500 м³/ч. Угольный фильтр от запахов."},
        ],
    },
    "mid": {
        "title": "⭐ Средний сегмент (3–8 млн)",
        "models": [
            {"id": "sam", "name": "Samsung AX60R5080WD", "price": "3 500 000", "price_num": 3500000, "area": "60 м²", "filter": "HEPA + Carbon", "desc": "3-ступенчатая фильтрация. Убирает запах дыма и животных. Wi-Fi."},
            {"id": "smp", "name": "Smartmi Air Purifier P1", "price": "4 200 000", "price_num": 4200000, "area": "55 м²", "filter": "HEPA H13 + Carbon", "desc": "Тихий как шёпот. Датчик CO2. Компактный и стильный дизайн."},
            {"id": "p17", "name": "Philips AC1715/10", "price": "5 290 000", "price_num": 5290000, "area": "78 м²", "filter": "NanoProtect HEPA", "desc": "NanoProtect HEPA. Режим сна. Датчик PM2.5 в реальном времени."},
            {"id": "p28", "name": "Philips AC2887/10", "price": "6 890 000", "price_num": 6890000, "area": "79 м²", "filter": "NanoProtect HEPA", "desc": "CADR 600 м³/ч. AeraSense датчик. Для больших помещений."},
            {"id": "dtp", "name": "Dyson Purifier Cool TP10", "price": "7 690 000", "price_num": 7690000, "area": "80 м²", "filter": "HEPA H13 + Carbon", "desc": "Вентилятор + очиститель 2в1. 360° фильтрация. Премиум-дизайн."},
            {"id": "blu", "name": "Blueair Classic 480i", "price": "8 500 000", "price_num": 8500000, "area": "40 м²", "filter": "HEPASilent + Carbon", "desc": "Шведский бренд №1. HEPASilent технология. Почти бесшумный."},
        ],
    },
    "premium": {
        "title": "💎 Премиум и промышленные (10+ млн)",
        "models": [
            {"id": "dph", "name": "Dyson PH04 Humidify+Cool", "price": "12 900 000", "price_num": 12900000, "area": "100 м²", "filter": "HEPA H13 + Carbon", "desc": "Очистка + увлажнение + охлаждение. Формальдегид-сенсор. До 100 м²."},
            {"id": "iq2", "name": "IQAir HealthPro 250", "price": "21 000 000", "price_num": 21000000, "area": "200 м²", "filter": "HyperHEPA H14", "desc": "Медицинский HyperHEPA H14. До 200 м². Швейцарское качество."},
            {"id": "air", "name": "Airdog X8 Commercial", "price": "28 000 000", "price_num": 28000000, "area": "300 м²", "filter": "TPA ионный", "desc": "CADR 1000 м³/ч. Моющийся фильтр (без замены). До 300 м²."},
        ],
    },
}

# Тарифы аренды — как на сайте (pricing.html)
RENTAL_PLANS = {
    "basic": {
        "name": "Базовый",
        "emoji": "🌱",
        "price": "180 000 сум/мес",
        "includes": [
            "Xiaomi 3C или 4 Lite",
            "Покрытие до 45 м²",
            "1 бесплатная замена фильтра",
            "Доставка и установка",
        ],
        "best_for": "Офис до 6 чел., салон красоты, кабинет",
    },
    "business": {
        "name": "Бизнес",
        "emoji": "💼",
        "price": "400 000 сум/мес",
        "includes": [
            "Philips AC1715 или Xiaomi 4 Pro",
            "Покрытие до 80 м²",
            "Замена фильтра каждые 6 мес",
            "Доставка и установка",
            "Замена модели без доплат",
            "Приложение для мониторинга",
        ],
        "best_for": "Кафе, коворкинг, школьный класс, офис до 20 чел.",
    },
    "enterprise": {
        "name": "Промышленный",
        "emoji": "🏢",
        "price": "от 1 200 000 сум/мес",
        "includes": [
            "IQAir HealthPro или 2× Dyson TP10",
            "Покрытие 200+ м²",
            "Комплексное обслуживание",
            "Датчики PM2.5 по периметру",
            "Ежемесячный отчёт",
            "Персональный менеджер",
        ],
        "best_for": "Детский сад, бизнес-центр, склад, цех",
    },
}

# Топ-5 для быстрого заказа
TOP_MODELS = [
    {"id": "x4p", "name": "Xiaomi 4 Pro", "price": "2 990 000 сум"},
    {"id": "p17", "name": "Philips AC1715", "price": "5 290 000 сум"},
    {"id": "dtp", "name": "Dyson TP10", "price": "7 690 000 сум"},
    {"id": "dph", "name": "Dyson PH04", "price": "12 900 000 сум"},
    {"id": "iq2", "name": "IQAir HealthPro 250", "price": "21 000 000 сум"},
]

UZ_CITIES = [
    ("Ташкент", "tashkent"),
    ("Самарканд", "samarkand"),
    ("Бухара", "bukhara"),
    ("Наманган", "namangan"),
    ("Фергана", "fergana"),
    ("Нукус", "nukus"),
    ("Андижан", "andijan"),
]

# ═══════════════════════════════════════════
#  FSM STATES
# ═══════════════════════════════════════════
class RentalState(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    confirm = State()

class OrderState(StatesGroup):
    waiting_address = State()
    confirm = State()

class AQIState(StatesGroup):
    waiting_city = State()

# ═══════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════
router = Router()

def aqi_emoji(aqi: int) -> str:
    if aqi <= 50: return "🟢"
    if aqi <= 100: return "🟡"
    if aqi <= 150: return "🟠"
    if aqi <= 200: return "🔴"
    if aqi <= 300: return "🟣"
    return "⬛"

def aqi_level(aqi: int) -> str:
    if aqi <= 50: return "Хороший"
    if aqi <= 100: return "Умеренный"
    if aqi <= 150: return "Вредный для уязвимых"
    if aqi <= 200: return "Вредный"
    if aqi <= 300: return "Очень вредный"
    return "Опасный"

def aqi_bar(aqi: int) -> str:
    blocks = {"good": "🟩", "mod": "🟨", "usg": "🟧", "bad": "🟥", "vbad": "🟪", "haz": "⬛"}
    if aqi <= 50: b = blocks["good"]
    elif aqi <= 100: b = blocks["mod"]
    elif aqi <= 150: b = blocks["usg"]
    elif aqi <= 200: b = blocks["bad"]
    elif aqi <= 300: b = blocks["vbad"]
    else: b = blocks["haz"]
    filled = min(aqi, 500) // 25
    return b * filled + "⬜" * (20 - filled)

def aqi_advice(aqi: int) -> str:
    if aqi <= 50: return "✅ Воздух чистый. Наслаждайтесь!"
    if aqi <= 100: return "😐 Приемлемо, но чувствительным лучше ограничить прогулки."
    if aqi <= 150: return "⚠️ Закройте окна. Рекомендуем очиститель воздуха."
    return "🚨 Опасно! Используйте очиститель, не открывайте окна."

def find_model(model_id: str) -> dict | None:
    for cat in CATALOG.values():
        for m in cat["models"]:
            if m["id"] == model_id:
                return m
    return None

async def fetch_aqi(city: str) -> dict | None:
    url = f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}"
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                data = await r.json()
                if data.get("status") == "ok":
                    return data["data"]
    except Exception:
        pass
    return None

# ═══════════════════════════════════════════
#  KEYBOARDS
# ═══════════════════════════════════════════
def kb_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌍 Проверить воздух", callback_data="aqi"),
         InlineKeyboardButton(text="🛒 Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="💳 Аренда", callback_data="rent_plans"),
         InlineKeyboardButton(text="📊 Калькулятор", callback_data="calc")],
        [InlineKeyboardButton(text="ℹ️ О нас", callback_data="about"),
         InlineKeyboardButton(text="📱 Сайт", web_app=WebAppInfo(url=WEBSITE))],
    ])

def kb_cities() -> InlineKeyboardMarkup:
    rows = []
    row = []
    for name, slug in UZ_CITIES:
        row.append(InlineKeyboardButton(text=name, callback_data=f"city_{slug}"))
        if len(row) == 3:
            rows.append(row); row = []
    if row: rows.append(row)
    rows.append([InlineKeyboardButton(text="✏️ Ввести вручную", callback_data="aqi_manual")])
    rows.append([InlineKeyboardButton(text="◀️ Меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def kb_back(text="◀️ Меню", data="menu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text, callback_data=data)]])

# ═══════════════════════════════════════════
#  /start
# ═══════════════════════════════════════════
@router.message(CommandStart())
async def cmd_start(msg: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    deep = command.args

    # Deep links от сайта
    if deep and deep.startswith("rent_"):
        plan_key = deep[5:]
        plan = RENTAL_PLANS.get(plan_key)
        if plan:
            items = "\n".join(f"  ✅ {i}" for i in plan["includes"])
            await msg.answer(
                f"{plan['emoji']} <b>Тариф «{plan['name']}»</b>\n\n"
                f"💰 <b>{plan['price']}</b>\n\n"
                f"📦 Что входит:\n{items}\n\n"
                f"👥 Подходит: {plan['best_for']}\n\n"
                f"Оформить аренду?",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Оформить", callback_data=f"rent_go_{plan_key}")],
                    [InlineKeyboardButton(text="💳 Все тарифы", callback_data="rent_plans")],
                    [InlineKeyboardButton(text="◀️ Меню", callback_data="menu")],
                ]))
            return

    if deep in ("order", "cart"):
        await msg.answer(
            "🛒 <b>Оформление заказа</b>\n\nВыберите модель:",
            reply_markup=_kb_top_models())
        await state.set_state(OrderState.waiting_address)
        return

    if deep == "contact":
        await msg.answer(
            "📞 <b>Контакты EcoAeris</b>\n\n"
            "📍 Ташкент, ул. Амира Темура, 108\n"
            "📞 +998 90 123-45-67\n"
            "⏰ Пн–Пт 9:00–18:00, Сб 10:00–16:00\n\n"
            "Или напишите прямо сюда — мы ответим!",
            reply_markup=kb_main())
        return

    # Обычный /start
    await msg.answer(
        "👋 <b>Добро пожаловать в EcoAeris!</b>\n\n"
        "🌍 Мониторинг воздуха по всему Узбекистану\n"
        "🛒 Каталог очистителей (12 моделей)\n"
        "💳 Аренда от 180 000 сум/мес\n"
        "📊 Подбор по площади и бюджету\n\n"
        "Выберите действие ⬇️",
        reply_markup=kb_main())

# ═══════════════════════════════════════════
#  /help, /cancel
# ═══════════════════════════════════════════
@router.message(Command("help"))
async def cmd_help(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "📖 <b>Команды:</b>\n\n"
        "/start — Главное меню\n"
        "/aqi — Проверить воздух\n"
        "/catalog — Каталог (12 моделей)\n"
        "/rent — Тарифы аренды\n"
        "/order — Заказать очиститель\n"
        "/cancel — Отменить действие",
        reply_markup=kb_main())

@router.message(Command("cancel"))
async def cmd_cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("❌ Отменено.", reply_markup=kb_main())

# ═══════════════════════════════════════════
#  /aqi
# ═══════════════════════════════════════════
@router.message(Command("aqi"))
async def cmd_aqi(msg: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    city = command.args
    if not city:
        await msg.answer("🌍 <b>Выберите город:</b>", reply_markup=kb_cities())
        return
    await _show_aqi(msg, city.strip())

async def _show_aqi(target, city: str):
    loading = await target.answer("⏳ Загружаю...")
    data = await fetch_aqi(city)
    if not data or not isinstance(data.get("aqi"), int):
        await loading.edit_text(
            f"❌ <b>«{city}» не найден</b>\n\nВведите город на английском: <code>tashkent</code>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Попробовать", callback_data="aqi_manual")],
                [InlineKeyboardButton(text="◀️ Меню", callback_data="menu")],
            ]))
        return

    aqi = data["aqi"]
    name = data.get("city", {}).get("name", city)
    iaqi = data.get("iaqi", {})
    time_s = data.get("time", {}).get("s", "")

    # Загрязнители
    poll = []
    for k, label in [("pm25","PM2.5"),("pm10","PM10"),("o3","O₃"),("no2","NO₂"),("co","CO")]:
        v = iaqi.get(k, {}).get("v")
        if v is not None: poll.append(f"  • {label}: <b>{v}</b>")

    temp = iaqi.get("t", {}).get("v")
    hum = iaqi.get("h", {}).get("v")
    weather = ""
    if temp is not None: weather += f"🌡 {temp}°C  "
    if hum is not None: weather += f"💧 {hum}%"

    text = (
        f"{aqi_emoji(aqi)} <b>{name}</b>\n\n"
        f"📊 <b>AQI: {aqi}</b> — {aqi_level(aqi)}\n"
        f"{aqi_bar(aqi)}\n"
    )
    if poll: text += "\n📋 Загрязнители:\n" + "\n".join(poll) + "\n"
    if weather: text += f"\n{weather}\n"
    text += f"\n{aqi_advice(aqi)}\n"
    if time_s: text += f"\n<i>Обновлено: {time_s}</i>"

    await loading.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Другой город", callback_data="aqi")],
        [InlineKeyboardButton(text="🛒 Подобрать очиститель", callback_data="catalog")],
        [InlineKeyboardButton(text="◀️ Меню", callback_data="menu")],
    ]))

# ═══════════════════════════════════════════
#  CATALOG
# ═══════════════════════════════════════════
@router.message(Command("catalog"))
async def cmd_catalog(msg: Message, state: FSMContext):
    await state.clear()
    await _show_categories(msg)

async def _show_categories(target):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Бюджетные (1.7–3 млн)", callback_data="cat_budget")],
        [InlineKeyboardButton(text="⭐ Средний (3.5–8.5 млн)", callback_data="cat_mid")],
        [InlineKeyboardButton(text="💎 Премиум (12–28 млн)", callback_data="cat_premium")],
        [InlineKeyboardButton(text="◀️ Меню", callback_data="menu")],
    ])
    text = "🛒 <b>Каталог очистителей</b>\n\n12 моделей · 8 брендов\nВыберите категорию:"
    if isinstance(target, CallbackQuery):
        await target.message.answer(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)

@router.callback_query(F.data.startswith("cat_"))
async def cb_cat(cb: CallbackQuery):
    cat = CATALOG.get(cb.data[4:])
    if not cat: await cb.answer("Не найдено"); return

    lines = [f"<b>{cat['title']}</b>\n"]
    buttons = []
    for m in cat["models"]:
        lines.append(f"• <b>{m['name']}</b>\n  💰 {m['price']} сум · 📐 {m['area']}")
        buttons.append([InlineKeyboardButton(text=f"🔍 {m['name']}", callback_data=f"mod_{m['id']}")])
    buttons.append([InlineKeyboardButton(text="◀️ Категории", callback_data="catalog")])

    await cb.message.answer("\n\n".join(lines), reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await cb.answer()

@router.callback_query(F.data.startswith("mod_"))
async def cb_model(cb: CallbackQuery):
    m = find_model(cb.data[4:])
    if not m: await cb.answer("Не найдено"); return

    await cb.message.answer(
        f"📦 <b>{m['name']}</b>\n\n"
        f"💰 Цена: <b>{m['price']} сум</b>\n"
        f"📐 Площадь: <b>{m['area']}</b>\n"
        f"🧪 Фильтр: <b>{m['filter']}</b>\n\n"
        f"📝 {m['desc']}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Заказать", callback_data=f"buy_{m['id']}")],
            [InlineKeyboardButton(text="◀️ Категории", callback_data="catalog")],
        ]))
    await cb.answer()

# ═══════════════════════════════════════════
#  RENTAL
# ═══════════════════════════════════════════
@router.message(Command("rent"))
async def cmd_rent(msg: Message, state: FSMContext):
    await state.clear()
    await _show_plans(msg)

async def _show_plans(target):
    buttons = []
    for key, p in RENTAL_PLANS.items():
        buttons.append([InlineKeyboardButton(
            text=f"{p['emoji']} {p['name']} — {p['price']}", callback_data=f"rent_info_{key}")])
    buttons.append([InlineKeyboardButton(text="◀️ Меню", callback_data="menu")])
    text = "💳 <b>Тарифы аренды</b>\n\nОт 180 000 сум/мес. Выберите тариф:"
    if isinstance(target, CallbackQuery):
        await target.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    else:
        await target.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data == "rent_plans")
async def cb_rent_plans(cb: CallbackQuery):
    await _show_plans(cb); await cb.answer()

@router.callback_query(F.data.startswith("rent_info_"))
async def cb_rent_info(cb: CallbackQuery):
    p = RENTAL_PLANS.get(cb.data[10:])
    if not p: await cb.answer("Не найдено"); return
    items = "\n".join(f"  ✅ {i}" for i in p["includes"])
    await cb.message.answer(
        f"{p['emoji']} <b>Тариф «{p['name']}»</b>\n\n"
        f"💰 <b>{p['price']}</b>\n\n📦 Что входит:\n{items}\n\n"
        f"👥 Подходит: {p['best_for']}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Оформить аренду", callback_data=f"rent_go_{cb.data[10:]}")],
            [InlineKeyboardButton(text="◀️ Все тарифы", callback_data="rent_plans")],
        ]))
    await cb.answer()

@router.callback_query(F.data.startswith("rent_go_"))
async def cb_rent_start(cb: CallbackQuery, state: FSMContext):
    p = RENTAL_PLANS.get(cb.data[8:])
    if not p: await cb.answer("Не найдено"); return
    await state.update_data(plan_key=cb.data[8:], plan_name=p["name"], plan_price=p["price"])
    await state.set_state(RentalState.waiting_name)
    await cb.message.answer(
        f"📝 <b>Оформление «{p['name']}»</b>\n\nШаг 1/2: Введите <b>ФИО</b>:\n\n<i>/cancel для отмены</i>")
    await cb.answer()

@router.message(RentalState.waiting_name, F.text)
async def rent_name(msg: Message, state: FSMContext):
    if len(msg.text.strip()) < 2:
        await msg.answer("⚠️ Слишком короткое. Введите полное ФИО:"); return
    await state.update_data(name=msg.text.strip())
    await state.set_state(RentalState.waiting_phone)
    await msg.answer("📱 Шаг 2/2: Введите <b>номер телефона</b>:\n\nНапример: <code>+998 90 123 45 67</code>")

@router.message(RentalState.waiting_phone, F.text)
async def rent_phone(msg: Message, state: FSMContext):
    digits = "".join(c for c in msg.text if c.isdigit())
    if len(digits) < 9:
        await msg.answer("⚠️ Введите корректный номер (+998...)"); return
    await state.update_data(phone=msg.text.strip())
    d = await state.get_data()
    await msg.answer(
        f"📋 <b>Подтверждение аренды</b>\n\n"
        f"💳 Тариф: <b>{d['plan_name']}</b>\n"
        f"💰 Стоимость: <b>{d['plan_price']}</b>\n"
        f"👤 Имя: <b>{d['name']}</b>\n"
        f"📱 Телефон: <b>{d['phone']}</b>\n\nВсё верно?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="rent_ok"),
             InlineKeyboardButton(text="❌ Отменить", callback_data="rent_no")],
        ]))
    await state.set_state(RentalState.confirm)

@router.callback_query(RentalState.confirm, F.data == "rent_ok")
async def rent_confirm(cb: CallbackQuery, state: FSMContext):
    d = await state.get_data(); await state.clear()
    oid = f"R-{cb.from_user.id}-{int(asyncio.get_event_loop().time())}"
    log.info("RENTAL: %s plan=%s name=%s phone=%s", oid, d["plan_name"], d["name"], d["phone"])
    await cb.message.answer(
        f"🎉 <b>Заявка принята!</b>\n\n"
        f"📧 Заявка: <code>{oid}</code>\n"
        f"💳 {d['plan_name']} — {d['plan_price']}\n"
        f"👤 {d['name']} · 📱 {d['phone']}\n\n"
        f"📞 Менеджер свяжется в течение 30 минут.",
        reply_markup=kb_back()); await cb.answer()

@router.callback_query(RentalState.confirm, F.data == "rent_no")
async def rent_cancel(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.answer("❌ Отменено.", reply_markup=kb_main()); await cb.answer()

# ═══════════════════════════════════════════
#  ORDER
# ═══════════════════════════════════════════
def _kb_top_models() -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=f"📦 {m['name']} — {m['price']}", callback_data=f"buy_{m['id']}")] for m in TOP_MODELS]
    rows.append([InlineKeyboardButton(text="🛒 Весь каталог", callback_data="catalog")])
    rows.append([InlineKeyboardButton(text="◀️ Меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

@router.message(Command("order"))
async def cmd_order(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("🛒 <b>Быстрый заказ</b>\n\nВыберите модель:", reply_markup=_kb_top_models())

@router.callback_query(F.data.startswith("buy_"))
async def cb_buy(cb: CallbackQuery, state: FSMContext):
    m = find_model(cb.data[4:])
    if not m: await cb.answer("Не найдено"); return
    await state.update_data(model=m["name"], price=m["price"])
    await state.set_state(OrderState.waiting_address)
    await cb.message.answer(
        f"📦 <b>{m['name']}</b> — {m['price']} сум\n\n📍 Введите <b>адрес доставки</b>:\n\n<i>/cancel для отмены</i>")
    await cb.answer()

@router.message(OrderState.waiting_address, F.text)
async def order_addr(msg: Message, state: FSMContext):
    if len(msg.text.strip()) < 5:
        await msg.answer("⚠️ Введите полный адрес"); return
    await state.update_data(addr=msg.text.strip())
    d = await state.get_data()
    await msg.answer(
        f"📋 <b>Подтверждение заказа</b>\n\n"
        f"📦 {d['model']}\n💰 {d['price']} сум\n📍 {d['addr']}\n\nВсё верно?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="ord_ok"),
             InlineKeyboardButton(text="❌ Отменить", callback_data="ord_no")],
        ]))
    await state.set_state(OrderState.confirm)

@router.callback_query(OrderState.confirm, F.data == "ord_ok")
async def order_ok(cb: CallbackQuery, state: FSMContext):
    d = await state.get_data(); await state.clear()
    oid = f"O-{cb.from_user.id}-{int(asyncio.get_event_loop().time())}"
    log.info("ORDER: %s model=%s addr=%s", oid, d["model"], d["addr"])
    await cb.message.answer(
        f"🎉 <b>Заказ оформлен!</b>\n\n"
        f"📧 Заказ: <code>{oid}</code>\n📦 {d['model']}\n💰 {d['price']} сум\n📍 {d['addr']}\n\n"
        f"🚚 Доставка 1-3 дня. Менеджер позвонит для подтверждения.",
        reply_markup=kb_back()); await cb.answer()

@router.callback_query(OrderState.confirm, F.data == "ord_no")
async def order_no(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.answer("❌ Заказ отменён.", reply_markup=kb_main()); await cb.answer()

# ═══════════════════════════════════════════
#  AQI CALLBACKS
# ═══════════════════════════════════════════
@router.callback_query(F.data == "aqi")
async def cb_aqi(cb: CallbackQuery):
    await cb.message.answer("🌍 <b>Выберите город:</b>", reply_markup=kb_cities()); await cb.answer()

@router.callback_query(F.data.startswith("city_"))
async def cb_city(cb: CallbackQuery):
    await _show_aqi(cb.message, cb.data[5:]); await cb.answer()

@router.callback_query(F.data == "aqi_manual")
async def cb_aqi_manual(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AQIState.waiting_city)
    await cb.message.answer("✏️ Введите город на английском:\n\n<code>tashkent</code>, <code>moscow</code>, <code>london</code>")
    await cb.answer()

@router.message(AQIState.waiting_city, F.text)
async def aqi_manual(msg: Message, state: FSMContext):
    if msg.text.startswith("/"): return
    await state.clear()
    await _show_aqi(msg, msg.text.strip())

# ═══════════════════════════════════════════
#  OTHER CALLBACKS
# ═══════════════════════════════════════════
@router.callback_query(F.data == "catalog")
async def cb_catalog(cb: CallbackQuery):
    await _show_categories(cb); await cb.answer()

@router.callback_query(F.data == "calc")
async def cb_calc(cb: CallbackQuery):
    await cb.message.answer(
        "📊 <b>Калькулятор подбора</b>\n\nОтветьте на 4 вопроса — получите рекомендацию:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Открыть калькулятор", web_app=WebAppInfo(url=f"{WEBSITE}/calculator.html"))],
            [InlineKeyboardButton(text="◀️ Меню", callback_data="menu")],
        ])); await cb.answer()

@router.callback_query(F.data == "about")
async def cb_about(cb: CallbackQuery):
    await cb.message.answer(
        "ℹ️ <b>EcoAeris</b>\n\n"
        "Первый в Узбекистане сервис мониторинга воздуха + подбор очистителей.\n\n"
        "📊 Данные из 500+ станций мира\n"
        "🛒 12 моделей от 1.7 до 28 млн сум\n"
        "💳 Аренда от 180 000 сум/мес\n"
        "📱 Telegram-бот + сайт\n\n"
        "👥 Команда: 6 студентов TEA3DBA2A",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Сайт", web_app=WebAppInfo(url=WEBSITE))],
            [InlineKeyboardButton(text="◀️ Меню", callback_data="menu")],
        ])); await cb.answer()

@router.callback_query(F.data == "menu")
async def cb_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.answer("🏠 <b>Главное меню</b>", reply_markup=kb_main()); await cb.answer()

# ═══════════════════════════════════════════
#  FALLBACK
# ═══════════════════════════════════════════
@router.message(F.text)
async def fallback(msg: Message):
    if msg.text.startswith("/"):
        await msg.answer("❓ Неизвестная команда. /help"); return
    await msg.answer("🤔 Используйте кнопки или /help", reply_markup=kb_main())

# ═══════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════
async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    from aiogram.types import BotCommand
    await bot.set_my_commands([
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="aqi", description="Проверить воздух"),
        BotCommand(command="catalog", description="Каталог (12 моделей)"),
        BotCommand(command="rent", description="Аренда от 180к/мес"),
        BotCommand(command="order", description="Заказать очиститель"),
        BotCommand(command="cancel", description="Отмена"),
        BotCommand(command="help", description="Помощь"),
    ])

    log.info("EcoAeris Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
