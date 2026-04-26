"""
EcoAeris Telegram Bot
Бот для мониторинга качества воздуха и аренды очистителей.
Powered by aiogram 3.x with FSM
"""

import asyncio
import logging
import sys

import aiohttp
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ──────────────────────────────────────────────
#  Configuration
# ──────────────────────────────────────────────
BOT_TOKEN = "8212922655:AAGmK8b9N9gmZ7MI5AfLiGTUQ30TXo-dtDs"
WAQI_TOKEN = "demo"
WAQI_API = "https://api.waqi.info"
WEBSITE = "https://sadot0.github.io/ecoaeris"

# ──────────────────────────────────────────────
#  Logging
# ──────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
#  Data: plans, catalog models
# ──────────────────────────────────────────────
RENTAL_PLANS = {
    "basic": {
        "name": "Basic",
        "emoji": "\U0001f331",
        "price": "290 000 сум/мес",
        "includes": [
            "1 очиститель EcoAeris Home",
            "Покрытие до 40 м\u00b2",
            "Бесплатная доставка",
            "Замена фильтров раз в 3 месяца",
            "Базовая техподдержка",
        ],
    },
    "business": {
        "name": "Business",
        "emoji": "\U0001f4bc",
        "price": "690 000 сум/мес",
        "includes": [
            "2 очистителя EcoAeris Pro",
            "Покрытие до 120 м\u00b2",
            "Бесплатная доставка и установка",
            "Замена фильтров раз в 2 месяца",
            "Приоритетная техподдержка 24/7",
            "Мониторинг качества воздуха онлайн",
        ],
    },
    "enterprise": {
        "name": "Enterprise",
        "emoji": "\U0001f3e2",
        "price": "1 490 000 сум/мес",
        "includes": [
            "5 очистителей EcoAeris Industrial",
            "Покрытие до 500 м\u00b2",
            "Бесплатная доставка, установка и настройка",
            "Ежемесячная замена фильтров",
            "Персональный менеджер",
            "Техподдержка 24/7 + выезд в течение 2 часов",
            "Подключение к системе мониторинга",
        ],
    },
}

CATALOG = {
    "budget": {
        "title": "\U0001f4b0 Бюджетные модели",
        "models": [
            {"id": "b1", "name": "EcoAeris Lite", "price": "1 990 000 сум", "area": "до 25 м\u00b2", "desc": "Компактный очиститель для небольших комнат. HEPA-фильтр, 3 режима, тихая работа (28 дБ). Идеален для спальни."},
            {"id": "b2", "name": "EcoAeris Mini", "price": "2 490 000 сум", "area": "до 30 м\u00b2", "desc": "Портативный очиститель с USB-зарядкой. HEPA + угольный фильтр. Авто-режим по датчику качества воздуха."},
            {"id": "b3", "name": "EcoAeris Start", "price": "2 990 000 сум", "area": "до 35 м\u00b2", "desc": "Надёжный очиститель начального уровня. HEPA-13, ионизатор, таймер. Подходит для квартиры-студии."},
        ],
    },
    "mid": {
        "title": "\u2B50 Средний сегмент",
        "models": [
            {"id": "m1", "name": "EcoAeris Home", "price": "4 990 000 сум", "area": "до 50 м\u00b2", "desc": "Для дома и небольшого офиса. HEPA-13 + угольный + фотокаталитический фильтр. Wi-Fi, управление через приложение."},
            {"id": "m2", "name": "EcoAeris Comfort", "price": "5 990 000 сум", "area": "до 60 м\u00b2", "desc": "Умный очиститель с датчиками PM2.5 и CO2. Авто-режим, ночной режим. Совместим с Алисой и Google Home."},
            {"id": "m3", "name": "EcoAeris Office", "price": "6 990 000 сум", "area": "до 75 м\u00b2", "desc": "Оптимальное решение для офиса. Два независимых фильтра, тихая работа (32 дБ), дисплей с показателями воздуха."},
            {"id": "m4", "name": "EcoAeris Family", "price": "7 490 000 сум", "area": "до 80 м\u00b2", "desc": "Семейная модель с детским замком и режимом \"Сон\". 5-ступенчатая очистка, увлажнение воздуха."},
        ],
    },
    "premium": {
        "title": "\U0001f451 Премиум модели",
        "models": [
            {"id": "p1", "name": "EcoAeris Pro", "price": "9 990 000 сум", "area": "до 100 м\u00b2", "desc": "Профессиональная модель. 6-ступенчатая очистка, UV-лампа, плазменный модуль. Полная автоматика."},
            {"id": "p2", "name": "EcoAeris Pro Max", "price": "12 990 000 сум", "area": "до 150 м\u00b2", "desc": "Топовая модель для больших пространств. Два мотора, рециркуляция 360\u00b0, медицинский HEPA-14."},
            {"id": "p3", "name": "EcoAeris Industrial", "price": "19 990 000 сум", "area": "до 300 м\u00b2", "desc": "Промышленный очиститель для складов, цехов и торговых центров. Металлический корпус, непрерывная работа 24/7."},
        ],
    },
}

# Top 5 models for quick order flow
TOP_MODELS = [
    {"id": "m1", "name": "EcoAeris Home", "price": "4 990 000 сум"},
    {"id": "m2", "name": "EcoAeris Comfort", "price": "5 990 000 сум"},
    {"id": "m3", "name": "EcoAeris Office", "price": "6 990 000 сум"},
    {"id": "p1", "name": "EcoAeris Pro", "price": "9 990 000 сум"},
    {"id": "p2", "name": "EcoAeris Pro Max", "price": "12 990 000 сум"},
]

UZ_CITIES = [
    ("Tashkent", "tashkent"),
    ("Samarkand", "samarkand"),
    ("Bukhara", "bukhara"),
    ("Namangan", "namangan"),
    ("Fergana", "fergana"),
]


# ──────────────────────────────────────────────
#  FSM States
# ──────────────────────────────────────────────
class RentalState(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    confirm = State()


class OrderState(StatesGroup):
    choosing_model = State()
    waiting_address = State()
    confirm = State()


class AQIState(StatesGroup):
    waiting_city = State()


# ──────────────────────────────────────────────
#  Router & helpers
# ──────────────────────────────────────────────
router = Router()


def aqi_color(aqi: int) -> str:
    if aqi <= 50:
        return "\U0001f7e2"
    elif aqi <= 100:
        return "\U0001f7e1"
    elif aqi <= 150:
        return "\U0001f7e0"
    elif aqi <= 200:
        return "\U0001f534"
    elif aqi <= 300:
        return "\U0001f7e3"
    else:
        return "\U0001f7e4"


def aqi_level_text(aqi: int) -> str:
    if aqi <= 50:
        return "Отличное — воздух чистый"
    elif aqi <= 100:
        return "Умеренное — приемлемо"
    elif aqi <= 150:
        return "Вредно для чувствительных групп"
    elif aqi <= 200:
        return "Вредно для здоровья"
    elif aqi <= 300:
        return "Очень вредно"
    else:
        return "Опасно!"


def aqi_bar(aqi: int) -> str:
    """Build a simple bar chart for AQI value (max 500 scale)."""
    filled = min(aqi, 500) // 25
    empty = 20 - filled
    if aqi <= 50:
        block = "\U0001f7e9"
    elif aqi <= 100:
        block = "\U0001f7e8"
    elif aqi <= 150:
        block = "\U0001f7e7"
    elif aqi <= 200:
        block = "\U0001f7e5"
    elif aqi <= 300:
        block = "\U0001f7ea"
    else:
        block = "\u2b1b"
    return block * filled + "\u2b1c" * empty


def main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="\U0001f30d Проверить AQI", callback_data="aqi"),
                InlineKeyboardButton(text="\U0001f6d2 Каталог", callback_data="catalog"),
            ],
            [
                InlineKeyboardButton(text="\U0001f4ca Калькулятор", callback_data="calculator"),
                InlineKeyboardButton(text="\u2139\ufe0f О нас", callback_data="about"),
            ],
            [
                InlineKeyboardButton(text="\U0001f4b3 Тарифы аренды", callback_data="rental_plans"),
            ],
            [
                InlineKeyboardButton(
                    text="\U0001f4f1 Открыть сайт",
                    web_app=WebAppInfo(url=WEBSITE),
                ),
            ],
        ]
    )


def city_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for label, code in UZ_CITIES:
        row.append(InlineKeyboardButton(text=f"\U0001f3d9 {label}", callback_data=f"city_{code}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="\u2328\ufe0f Ввести вручную", callback_data="aqi_manual")])
    buttons.append([InlineKeyboardButton(text="\u25c0\ufe0f Назад в меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def fetch_aqi(city: str) -> dict | None:
    url = f"{WAQI_API}/feed/{city}/?token={WAQI_TOKEN}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                data = await resp.json()
                if data.get("status") == "ok":
                    return data["data"]
    except Exception as e:
        logger.error("WAQI API error: %s", e)
    return None


def format_aqi_message(data: dict) -> str:
    aqi = data.get("aqi", "N/A")
    city_name = data.get("city", {}).get("name", "Неизвестно")
    time_str = data.get("time", {}).get("s", "")

    if not isinstance(aqi, int):
        return (
            f"\u26a0\ufe0f <b>Не удалось получить AQI</b>\n\n"
            f"Для города <b>{city_name}</b> данные временно недоступны.\n"
            f"Попробуйте позже или введите другой город."
        )

    color = aqi_color(aqi)
    level = aqi_level_text(aqi)
    bar = aqi_bar(aqi)

    iaqi = data.get("iaqi", {})
    pollutants_lines = []
    pollutant_names = {
        "pm25": "PM2.5",
        "pm10": "PM10",
        "o3": "O\u2083",
        "no2": "NO\u2082",
        "so2": "SO\u2082",
        "co": "CO",
    }
    for key, label in pollutant_names.items():
        val = iaqi.get(key, {}).get("v")
        if val is not None:
            pollutants_lines.append(f"  \u2022 {label}: <b>{val}</b>")

    pollutants_block = "\n".join(pollutants_lines)
    if pollutants_block:
        pollutants_block = f"\n\n\U0001f4cb <b>Загрязнители:</b>\n{pollutants_block}"

    extras = []
    temp = iaqi.get("t", {}).get("v")
    hum = iaqi.get("h", {}).get("v")
    if temp is not None:
        extras.append(f"\U0001f321 Температура: <b>{temp}\u00b0C</b>")
    if hum is not None:
        extras.append(f"\U0001f4a7 Влажность: <b>{hum}%</b>")
    extras_block = "\n".join(extras)
    if extras_block:
        extras_block = f"\n\n{extras_block}"

    recommendation = ""
    if aqi > 100:
        recommendation = "\n\n\u26a0\ufe0f <b>Рекомендуем использовать очиститель воздуха!</b>"
    else:
        recommendation = "\n\n\u2705 Воздух в пределах нормы."

    return (
        f"{color} <b>Качество воздуха — {city_name}</b>\n\n"
        f"\U0001f522 <b>AQI: {aqi}</b>\n"
        f"{bar}\n"
        f"\U0001f4ca Уровень: <i>{level}</i>\n"
        f"\U0001f550 Обновлено: {time_str}"
        f"{pollutants_block}"
        f"{extras_block}"
        f"{recommendation}"
    )


# ──────────────────────────────────────────────
#  /start with deep-link support
# ──────────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    # Clear any active state on /start
    await state.clear()
    deep = command.args

    if deep == "website":
        await message.answer(
            f"\U0001f4f1 <b>Добро пожаловать!</b>\n\n"
            f"Откройте наш сайт, чтобы узнать больше об EcoAeris:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="\U0001f310 Открыть сайт", web_app=WebAppInfo(url=WEBSITE))]
                ]
            ),
        )
        return

    if deep == "calc_result":
        await message.answer(
            f"\U0001f4ca <b>Калькулятор экономии</b>\n\n"
            f"Рассчитайте, сколько вы сэкономите с очистителем воздуха EcoAeris:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="\U0001f4ca Открыть калькулятор", web_app=WebAppInfo(url=f"{WEBSITE}/calculator.html"))]
                ]
            ),
        )
        return

    if deep == "contact":
        await message.answer(
            f"\U0001f4de <b>Свяжитесь с нами</b>\n\n"
            f"Мы всегда рады помочь! Напишите нам через форму на сайте\n"
            f"или свяжитесь напрямую:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="\U0001f4de Контакты", web_app=WebAppInfo(url=f"{WEBSITE}/contact.html"))]
                ]
            ),
        )
        return

    # ── Deep links: rental plans ──
    if deep and deep.startswith("rent_"):
        plan_key = deep[5:]  # basic / business / enterprise
        plan = RENTAL_PLANS.get(plan_key)
        if plan:
            includes_text = "\n".join(f"  \u2705 {item}" for item in plan["includes"])
            await message.answer(
                f"{plan['emoji']} <b>Тариф {plan['name']}</b>\n\n"
                f"\U0001f4b0 Стоимость: <b>{plan['price']}</b>\n\n"
                f"\U0001f4e6 <b>Что входит:</b>\n{includes_text}\n\n"
                f"Хотите оформить аренду?",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="\u2705 Оформить аренду", callback_data=f"rent_start_{plan_key}")],
                        [InlineKeyboardButton(text="\U0001f4b3 Все тарифы", callback_data="rental_plans")],
                        [InlineKeyboardButton(text="\u25c0\ufe0f Главное меню", callback_data="menu")],
                    ]
                ),
            )
            return

    # ── Deep links: order / cart ──
    if deep in ("order", "cart"):
        await message.answer(
            f"\U0001f6d2 <b>Оформление заказа</b>\n\n"
            f"Добро пожаловать! Мы поможем вам выбрать\n"
            f"идеальный очиститель воздуха.\n\n"
            f"Выберите модель из наших бестселлеров \u2b07\ufe0f",
            reply_markup=_top_models_keyboard(),
        )
        await state.set_state(OrderState.choosing_model)
        return

    # ── Default /start ──
    await message.answer(
        f"\U0001f44b <b>Добро пожаловать в EcoAeris!</b>\n\n"
        f"\U0001f33f Мы помогаем следить за качеством воздуха\n"
        f"и предлагаем аренду профессиональных очистителей.\n\n"
        f"<b>Что умеет этот бот:</b>\n"
        f"\U0001f30d Проверить качество воздуха в любом городе\n"
        f"\U0001f6d2 Просмотреть каталог очистителей\n"
        f"\U0001f4b3 Оформить аренду\n"
        f"\U0001f4ca Рассчитать экономию\n"
        f"\u2139\ufe0f Узнать о компании\n\n"
        f"Выберите действие \u2b07\ufe0f",
        reply_markup=main_keyboard(),
    )


# ──────────────────────────────────────────────
#  /help
# ──────────────────────────────────────────────
@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"\U0001f4d6 <b>Список команд:</b>\n\n"
        f"/start — Главное меню\n"
        f"/aqi — Проверить AQI (пример: /aqi tashkent)\n"
        f"/catalog — Каталог очистителей\n"
        f"/rent — Оформить аренду\n"
        f"/order — Заказать очиститель\n"
        f"/cancel — Отменить текущее действие\n"
        f"/help — Показать это сообщение",
        reply_markup=main_keyboard(),
    )


# ──────────────────────────────────────────────
#  /cancel — exit any FSM state
# ──────────────────────────────────────────────
@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    current = await state.get_state()
    await state.clear()
    if current:
        await message.answer(
            "\u274c Действие отменено.\n\nВозвращаемся в главное меню:",
            reply_markup=main_keyboard(),
        )
    else:
        await message.answer(
            "\U0001f914 Нечего отменять. Вот главное меню:",
            reply_markup=main_keyboard(),
        )


# ──────────────────────────────────────────────
#  /aqi [city]
# ──────────────────────────────────────────────
@router.message(Command("aqi"))
async def cmd_aqi(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    city = command.args
    if not city:
        await message.answer(
            "\U0001f30d <b>Проверка качества воздуха</b>\n\n"
            "Выберите город из списка или введите название вручную:",
            reply_markup=city_keyboard(),
        )
        return

    loading = await message.answer("\u23f3 Загрузка данных...")
    data = await fetch_aqi(city.strip())
    if data:
        await loading.edit_text(format_aqi_message(data))
    else:
        await loading.edit_text(
            f"\u274c <b>Город \u00ab{city}\u00bb не найден</b>\n\n"
            f"Попробуйте ввести название на английском языке.\n"
            f"Пример: <code>tashkent</code>"
        )


# ──────────────────────────────────────────────
#  /catalog
# ──────────────────────────────────────────────
@router.message(Command("catalog"))
async def cmd_catalog(message: Message, state: FSMContext):
    await state.clear()
    await _show_catalog_categories(message)


# ──────────────────────────────────────────────
#  /rent
# ──────────────────────────────────────────────
@router.message(Command("rent"))
async def cmd_rent(message: Message, state: FSMContext):
    await state.clear()
    await _show_rental_plans(message)


# ──────────────────────────────────────────────
#  /order
# ──────────────────────────────────────────────
@router.message(Command("order"))
async def cmd_order(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"\U0001f6d2 <b>Оформление заказа</b>\n\n"
        f"Выберите модель из наших бестселлеров \u2b07\ufe0f",
        reply_markup=_top_models_keyboard(),
    )
    await state.set_state(OrderState.choosing_model)


# ══════════════════════════════════════════════
#  CATALOG BROWSING
# ══════════════════════════════════════════════

async def _show_catalog_categories(target: Message | CallbackQuery):
    """Show catalog category buttons."""
    text = (
        f"\U0001f6d2 <b>Каталог очистителей воздуха</b>\n\n"
        f"Выберите категорию \u2b07\ufe0f"
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="\U0001f4b0 Бюджетные (от 1.99 млн)", callback_data="cat_budget")],
            [InlineKeyboardButton(text="\u2b50 Средний сегмент (от 4.99 млн)", callback_data="cat_mid")],
            [InlineKeyboardButton(text="\U0001f451 Премиум (от 9.99 млн)", callback_data="cat_premium")],
            [InlineKeyboardButton(text="\u25c0\ufe0f Назад в меню", callback_data="menu")],
        ]
    )
    if isinstance(target, CallbackQuery):
        await target.message.answer(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("cat_"))
async def cb_catalog_category(callback: CallbackQuery):
    category_key = callback.data[4:]  # budget / mid / premium
    category = CATALOG.get(category_key)
    if not category:
        await callback.answer("Категория не найдена", show_alert=True)
        return

    lines = [f"{category['title']}\n"]
    buttons = []
    for model in category["models"]:
        lines.append(
            f"\u2022 <b>{model['name']}</b>\n"
            f"  \U0001f4b0 {model['price']} | \U0001f4cf {model['area']}"
        )
        buttons.append(
            [InlineKeyboardButton(text=f"\U0001f50d {model['name']}", callback_data=f"model_{model['id']}")]
        )

    buttons.append([InlineKeyboardButton(text="\u25c0\ufe0f К категориям", callback_data="catalog")])
    buttons.append([InlineKeyboardButton(text="\U0001f3e0 Главное меню", callback_data="menu")])

    await callback.message.answer(
        "\n\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("model_"))
async def cb_model_detail(callback: CallbackQuery):
    model_id = callback.data[6:]
    model = _find_model(model_id)
    if not model:
        await callback.answer("Модель не найдена", show_alert=True)
        return

    await callback.message.answer(
        f"\U0001f4e6 <b>{model['name']}</b>\n\n"
        f"\U0001f4b0 Цена: <b>{model['price']}</b>\n"
        f"\U0001f4cf Площадь: <b>{model['area']}</b>\n\n"
        f"\U0001f4dd {model['desc']}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="\U0001f6d2 Заказать эту модель", callback_data=f"order_model_{model_id}")],
                [InlineKeyboardButton(text="\u25c0\ufe0f К категориям", callback_data="catalog")],
                [InlineKeyboardButton(text="\U0001f3e0 Главное меню", callback_data="menu")],
            ]
        ),
    )
    await callback.answer()


def _find_model(model_id: str) -> dict | None:
    for cat in CATALOG.values():
        for m in cat["models"]:
            if m["id"] == model_id:
                return m
    return None


# ══════════════════════════════════════════════
#  RENTAL FLOW (FSM)
# ══════════════════════════════════════════════

async def _show_rental_plans(target: Message | CallbackQuery):
    text = (
        f"\U0001f4b3 <b>Тарифы аренды очистителей</b>\n\n"
        f"Выберите подходящий тарифный план \u2b07\ufe0f"
    )
    buttons = []
    for key, plan in RENTAL_PLANS.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{plan['emoji']} {plan['name']} — {plan['price']}",
                callback_data=f"rent_info_{key}",
            )
        ])
    buttons.append([InlineKeyboardButton(text="\u25c0\ufe0f Назад в меню", callback_data="menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    if isinstance(target, CallbackQuery):
        await target.message.answer(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


@router.callback_query(F.data == "rental_plans")
async def cb_rental_plans(callback: CallbackQuery):
    await _show_rental_plans(callback)
    await callback.answer()


@router.callback_query(F.data.startswith("rent_info_"))
async def cb_rent_info(callback: CallbackQuery):
    plan_key = callback.data[10:]
    plan = RENTAL_PLANS.get(plan_key)
    if not plan:
        await callback.answer("Тариф не найден", show_alert=True)
        return

    includes_text = "\n".join(f"  \u2705 {item}" for item in plan["includes"])
    await callback.message.answer(
        f"{plan['emoji']} <b>Тариф {plan['name']}</b>\n\n"
        f"\U0001f4b0 Стоимость: <b>{plan['price']}</b>\n\n"
        f"\U0001f4e6 <b>Что входит:</b>\n{includes_text}\n\n"
        f"Хотите оформить аренду?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="\u2705 Оформить аренду", callback_data=f"rent_start_{plan_key}")],
                [InlineKeyboardButton(text="\u25c0\ufe0f Все тарифы", callback_data="rental_plans")],
                [InlineKeyboardButton(text="\U0001f3e0 Главное меню", callback_data="menu")],
            ]
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("rent_start_"))
async def cb_rent_start(callback: CallbackQuery, state: FSMContext):
    plan_key = callback.data[11:]
    plan = RENTAL_PLANS.get(plan_key)
    if not plan:
        await callback.answer("Тариф не найден", show_alert=True)
        return

    await state.update_data(plan_key=plan_key, plan_name=plan["name"], plan_price=plan["price"])
    await state.set_state(RentalState.waiting_name)
    await callback.message.answer(
        f"\U0001f4dd <b>Оформление аренды — {plan['name']}</b>\n\n"
        f"Шаг 1/2: Введите ваше <b>имя</b> (ФИО):\n\n"
        f"<i>Для отмены введите /cancel</i>"
    )
    await callback.answer()


@router.message(RentalState.waiting_name, F.text)
async def rental_get_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("\u26a0\ufe0f Имя слишком короткое. Пожалуйста, введите ваше ФИО:")
        return
    await state.update_data(customer_name=name)
    await state.set_state(RentalState.waiting_phone)
    await message.answer(
        f"\U0001f4f1 Шаг 2/2: Введите ваш <b>номер телефона</b>:\n\n"
        f"Например: <code>+998 90 123 45 67</code>\n\n"
        f"<i>Для отмены введите /cancel</i>"
    )


@router.message(RentalState.waiting_phone, F.text)
async def rental_get_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    # Basic validation: at least 7 digits
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) < 7:
        await message.answer(
            "\u26a0\ufe0f Неверный формат номера. Пожалуйста, введите корректный номер телефона:"
        )
        return

    await state.update_data(customer_phone=phone)
    data = await state.get_data()

    # Show confirmation
    await message.answer(
        f"\U0001f4cb <b>Подтверждение заявки на аренду</b>\n\n"
        f"\U0001f4b3 Тариф: <b>{data['plan_name']}</b>\n"
        f"\U0001f4b0 Стоимость: <b>{data['plan_price']}</b>\n\n"
        f"\U0001f464 Имя: <b>{data['customer_name']}</b>\n"
        f"\U0001f4f1 Телефон: <b>{data['customer_phone']}</b>\n\n"
        f"Всё верно?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="\u2705 Подтвердить", callback_data="rent_confirm"),
                    InlineKeyboardButton(text="\u274c Отменить", callback_data="rent_cancel"),
                ],
            ]
        ),
    )
    await state.set_state(RentalState.confirm)


@router.callback_query(RentalState.confirm, F.data == "rent_confirm")
async def cb_rent_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    order_id = f"R-{callback.from_user.id}-{int(asyncio.get_event_loop().time())}"

    await callback.message.answer(
        f"\U0001f389 <b>Заявка на аренду принята!</b>\n\n"
        f"\U0001f4e7 Номер заявки: <code>{order_id}</code>\n"
        f"\U0001f4b3 Тариф: <b>{data['plan_name']}</b>\n"
        f"\U0001f4b0 Стоимость: <b>{data['plan_price']}</b>\n"
        f"\U0001f464 Имя: <b>{data['customer_name']}</b>\n"
        f"\U0001f4f1 Телефон: <b>{data['customer_phone']}</b>\n\n"
        f"\U0001f4de Наш менеджер свяжется с вами в ближайшее время\n"
        f"для уточнения деталей доставки и подключения.\n\n"
        f"Спасибо, что выбрали EcoAeris!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="\U0001f3e0 Главное меню", callback_data="menu")],
            ]
        ),
    )
    logger.info(
        "NEW RENTAL: order=%s plan=%s name=%s phone=%s user_id=%s",
        order_id, data["plan_name"], data["customer_name"], data["customer_phone"], callback.from_user.id,
    )
    await callback.answer()


@router.callback_query(RentalState.confirm, F.data == "rent_cancel")
async def cb_rent_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "\u274c Заявка отменена.\n\nВозвращаемся в главное меню:",
        reply_markup=main_keyboard(),
    )
    await callback.answer()


# ══════════════════════════════════════════════
#  ORDER FLOW (FSM)
# ══════════════════════════════════════════════

def _top_models_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for m in TOP_MODELS:
        buttons.append([
            InlineKeyboardButton(
                text=f"\U0001f4e6 {m['name']} — {m['price']}",
                callback_data=f"order_select_{m['id']}",
            )
        ])
    buttons.append([InlineKeyboardButton(text="\U0001f6d2 Весь каталог", callback_data="catalog")])
    buttons.append([InlineKeyboardButton(text="\u25c0\ufe0f Назад в меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data.startswith("order_model_"))
async def cb_order_from_catalog(callback: CallbackQuery, state: FSMContext):
    """Start order flow from catalog model detail page."""
    model_id = callback.data[12:]
    model = _find_model(model_id)
    if not model:
        await callback.answer("Модель не найдена", show_alert=True)
        return
    await state.update_data(model_name=model["name"], model_price=model["price"])
    await state.set_state(OrderState.waiting_address)
    await callback.message.answer(
        f"\U0001f4e6 Вы выбрали: <b>{model['name']}</b> ({model['price']})\n\n"
        f"\U0001f4cd Введите <b>адрес доставки</b>:\n\n"
        f"<i>Для отмены введите /cancel</i>"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("order_select_"))
async def cb_order_select(callback: CallbackQuery, state: FSMContext):
    model_id = callback.data[13:]
    # Find in top models or catalog
    model = None
    for m in TOP_MODELS:
        if m["id"] == model_id:
            model = m
            break
    if not model:
        model = _find_model(model_id)
    if not model:
        await callback.answer("Модель не найдена", show_alert=True)
        return

    await state.update_data(model_name=model["name"], model_price=model["price"])
    await state.set_state(OrderState.waiting_address)
    await callback.message.answer(
        f"\U0001f4e6 Вы выбрали: <b>{model['name']}</b> ({model['price']})\n\n"
        f"\U0001f4cd Введите <b>адрес доставки</b>:\n\n"
        f"<i>Для отмены введите /cancel</i>"
    )
    await callback.answer()


@router.message(OrderState.waiting_address, F.text)
async def order_get_address(message: Message, state: FSMContext):
    address = message.text.strip()
    if len(address) < 5:
        await message.answer("\u26a0\ufe0f Адрес слишком короткий. Пожалуйста, введите полный адрес доставки:")
        return

    await state.update_data(address=address)
    data = await state.get_data()

    await message.answer(
        f"\U0001f4cb <b>Подтверждение заказа</b>\n\n"
        f"\U0001f4e6 Модель: <b>{data['model_name']}</b>\n"
        f"\U0001f4b0 Цена: <b>{data['model_price']}</b>\n"
        f"\U0001f4cd Адрес: <b>{data['address']}</b>\n\n"
        f"Всё верно?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="\u2705 Подтвердить", callback_data="order_confirm"),
                    InlineKeyboardButton(text="\u274c Отменить", callback_data="order_cancel"),
                ],
            ]
        ),
    )
    await state.set_state(OrderState.confirm)


@router.callback_query(OrderState.confirm, F.data == "order_confirm")
async def cb_order_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    order_id = f"O-{callback.from_user.id}-{int(asyncio.get_event_loop().time())}"

    await callback.message.answer(
        f"\U0001f389 <b>Заказ оформлен!</b>\n\n"
        f"\U0001f4e7 Номер заказа: <code>{order_id}</code>\n"
        f"\U0001f4e6 Модель: <b>{data['model_name']}</b>\n"
        f"\U0001f4b0 Цена: <b>{data['model_price']}</b>\n"
        f"\U0001f4cd Адрес: <b>{data['address']}</b>\n\n"
        f"\U0001f69a Доставка в течение 2-3 рабочих дней.\n"
        f"\U0001f4de Наш менеджер свяжется с вами для подтверждения.\n\n"
        f"Спасибо за заказ!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="\U0001f3e0 Главное меню", callback_data="menu")],
            ]
        ),
    )
    logger.info(
        "NEW ORDER: order=%s model=%s price=%s address=%s user_id=%s",
        order_id, data["model_name"], data["model_price"], data["address"], callback.from_user.id,
    )
    await callback.answer()


@router.callback_query(OrderState.confirm, F.data == "order_cancel")
async def cb_order_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "\u274c Заказ отменён.\n\nВозвращаемся в главное меню:",
        reply_markup=main_keyboard(),
    )
    await callback.answer()


# ══════════════════════════════════════════════
#  AQI CALLBACKS
# ══════════════════════════════════════════════

@router.callback_query(F.data == "aqi")
async def cb_aqi(callback: CallbackQuery):
    await callback.message.answer(
        "\U0001f30d <b>Проверка качества воздуха</b>\n\n"
        "Выберите город из списка или введите название вручную:",
        reply_markup=city_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("city_"))
async def cb_city_select(callback: CallbackQuery, state: FSMContext):
    city = callback.data[5:]
    loading = await callback.message.answer("\u23f3 Загрузка данных...")
    data = await fetch_aqi(city)
    if data:
        await loading.edit_text(format_aqi_message(data))
    else:
        await loading.edit_text(
            f"\u274c <b>Данные для \u00ab{city}\u00bb временно недоступны</b>\n\n"
            f"Попробуйте позже."
        )
    await callback.answer()


@router.callback_query(F.data == "aqi_manual")
async def cb_aqi_manual(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AQIState.waiting_city)
    await callback.message.answer(
        "\u2328\ufe0f <b>Введите название города</b>\n\n"
        "Например: <code>tashkent</code>, <code>moscow</code>, <code>london</code>\n\n"
        "<i>Для отмены введите /cancel</i>"
    )
    await callback.answer()


@router.message(AQIState.waiting_city, F.text)
async def aqi_manual_city(message: Message, state: FSMContext):
    if message.text.startswith("/"):
        return
    city = message.text.strip()
    await state.clear()
    loading = await message.answer("\u23f3 Загрузка данных...")
    data = await fetch_aqi(city)
    if data:
        await loading.edit_text(format_aqi_message(data))
    else:
        await loading.edit_text(
            f"\u274c <b>Город \u00ab{city}\u00bb не найден</b>\n\n"
            f"Попробуйте ввести название на английском языке.\n"
            f"Пример: <code>tashkent</code>",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="\U0001f504 Попробовать снова", callback_data="aqi_manual")],
                    [InlineKeyboardButton(text="\U0001f3e0 Главное меню", callback_data="menu")],
                ]
            ),
        )


# ══════════════════════════════════════════════
#  OTHER CALLBACKS
# ══════════════════════════════════════════════

@router.callback_query(F.data == "catalog")
async def cb_catalog(callback: CallbackQuery):
    await _show_catalog_categories(callback)
    await callback.answer()


@router.callback_query(F.data == "calculator")
async def cb_calculator(callback: CallbackQuery):
    await callback.message.answer(
        f"\U0001f4ca <b>Калькулятор экономии</b>\n\n"
        f"Узнайте, сколько вы сэкономите, используя\n"
        f"очиститель воздуха EcoAeris:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="\U0001f4ca Открыть калькулятор", web_app=WebAppInfo(url=f"{WEBSITE}/calculator.html"))],
                [InlineKeyboardButton(text="\u25c0\ufe0f Назад в меню", callback_data="menu")],
            ]
        ),
    )
    await callback.answer()


@router.callback_query(F.data == "about")
async def cb_about(callback: CallbackQuery):
    await callback.message.answer(
        f"\u2139\ufe0f <b>О компании EcoAeris</b>\n\n"
        f"\U0001f33f <b>EcoAeris</b> — сервис мониторинга качества воздуха\n"
        f"и аренды профессиональных очистителей.\n\n"
        f"\u2705 Мониторинг AQI в реальном времени\n"
        f"\u2705 Аренда очистителей для дома и офиса\n"
        f"\u2705 Гибкие тарифные планы\n"
        f"\u2705 Профессиональное обслуживание\n\n"
        f"Узнайте больше на нашем сайте:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="\U0001f310 О нас", web_app=WebAppInfo(url=f"{WEBSITE}/about.html"))],
                [InlineKeyboardButton(text="\U0001f4de Контакты", web_app=WebAppInfo(url=f"{WEBSITE}/contact.html"))],
                [InlineKeyboardButton(text="\u25c0\ufe0f Назад в меню", callback_data="menu")],
            ]
        ),
    )
    await callback.answer()


@router.callback_query(F.data == "menu")
async def cb_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "\U0001f3e0 <b>Главное меню</b>\n\nВыберите действие \u2b07\ufe0f",
        reply_markup=main_keyboard(),
    )
    await callback.answer()


# ──────────────────────────────────────────────
#  Fallback: handle text outside FSM
# ──────────────────────────────────────────────
@router.message(F.text)
async def handle_text(message: Message, state: FSMContext):
    text = message.text.strip()

    if text.startswith("/"):
        await message.answer(
            "\u2753 Неизвестная команда. Введите /help для списка команд."
        )
        return

    # Outside any FSM state — show menu
    await message.answer(
        f"\U0001f914 Не совсем понял.\n\n"
        f"Используйте кнопки меню или введите /help для списка команд.",
        reply_markup=main_keyboard(),
    )


# ──────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────
async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)

    logger.info("EcoAeris Bot started")

    from aiogram.types import BotCommand
    await bot.set_my_commands([
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="aqi", description="Проверить качество воздуха"),
        BotCommand(command="catalog", description="Каталог очистителей"),
        BotCommand(command="rent", description="Оформить аренду"),
        BotCommand(command="order", description="Заказать очиститель"),
        BotCommand(command="cancel", description="Отменить действие"),
        BotCommand(command="help", description="Помощь"),
    ])

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
