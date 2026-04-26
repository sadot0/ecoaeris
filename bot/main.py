"""
EcoAeris Telegram Bot
Бот для мониторинга качества воздуха и аренды очистителей.
Powered by aiogram 3.x
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
#  Router & helpers
# ──────────────────────────────────────────────
router = Router()

# Track users who are expected to type a city name
waiting_for_city: set[int] = set()


def aqi_color(aqi: int) -> str:
    """Return an emoji indicator based on AQI level."""
    if aqi <= 50:
        return "🟢"
    elif aqi <= 100:
        return "🟡"
    elif aqi <= 150:
        return "🟠"
    elif aqi <= 200:
        return "🔴"
    elif aqi <= 300:
        return "🟣"
    else:
        return "🟤"


def aqi_level_text(aqi: int) -> str:
    """Human-readable AQI level in Russian."""
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


def main_keyboard() -> InlineKeyboardMarkup:
    """Build the main menu inline keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🌍 Проверить AQI", callback_data="aqi"),
                InlineKeyboardButton(text="🛒 Каталог", callback_data="catalog"),
            ],
            [
                InlineKeyboardButton(text="📊 Калькулятор", callback_data="calculator"),
                InlineKeyboardButton(text="ℹ️ О нас", callback_data="about"),
            ],
            [
                InlineKeyboardButton(
                    text="📱 Открыть сайт",
                    web_app=WebAppInfo(url=WEBSITE),
                ),
            ],
        ]
    )


async def fetch_aqi(city: str) -> dict | None:
    """Fetch AQI data from WAQI API for the given city."""
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
    """Format AQI data into a nice Telegram message."""
    aqi = data.get("aqi", "N/A")
    city_name = data.get("city", {}).get("name", "Неизвестно")
    time_str = data.get("time", {}).get("s", "")

    if not isinstance(aqi, int):
        return (
            f"⚠️ <b>Не удалось получить AQI</b>\n\n"
            f"Для города <b>{city_name}</b> данные временно недоступны.\n"
            f"Попробуйте позже или введите другой город."
        )

    color = aqi_color(aqi)
    level = aqi_level_text(aqi)

    # Extract pollutant details if available
    iaqi = data.get("iaqi", {})
    pollutants_lines = []
    pollutant_names = {
        "pm25": "PM2.5",
        "pm10": "PM10",
        "o3": "O₃",
        "no2": "NO₂",
        "so2": "SO₂",
        "co": "CO",
    }
    for key, label in pollutant_names.items():
        val = iaqi.get(key, {}).get("v")
        if val is not None:
            pollutants_lines.append(f"  • {label}: <b>{val}</b>")

    pollutants_block = "\n".join(pollutants_lines)
    if pollutants_block:
        pollutants_block = f"\n\n📋 <b>Загрязнители:</b>\n{pollutants_block}"

    # Temperature & humidity
    extras = []
    temp = iaqi.get("t", {}).get("v")
    hum = iaqi.get("h", {}).get("v")
    if temp is not None:
        extras.append(f"🌡 Температура: <b>{temp}°C</b>")
    if hum is not None:
        extras.append(f"💧 Влажность: <b>{hum}%</b>")
    extras_block = "\n".join(extras)
    if extras_block:
        extras_block = f"\n\n{extras_block}"

    return (
        f"{color} <b>Качество воздуха — {city_name}</b>\n\n"
        f"🔢 <b>AQI: {aqi}</b>\n"
        f"📊 Уровень: <i>{level}</i>\n"
        f"🕐 Обновлено: {time_str}"
        f"{pollutants_block}"
        f"{extras_block}\n\n"
        f"{'⚠️ <b>Рекомендуем использовать очиститель воздуха!</b>' if aqi > 100 else '✅ Воздух в пределах нормы.'}"
    )


# ──────────────────────────────────────────────
#  /start with deep-link support
# ──────────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    deep = command.args  # e.g. "website", "order", "calc_result", etc.

    if deep == "website":
        await message.answer(
            f"📱 <b>Добро пожаловать!</b>\n\n"
            f"Откройте наш сайт, чтобы узнать больше об EcoAeris:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🌐 Открыть сайт", web_app=WebAppInfo(url=WEBSITE))]
                ]
            ),
        )
        return

    if deep == "order":
        await message.answer(
            f"🛒 <b>Оформление заказа</b>\n\n"
            f"Перейдите в наш каталог, чтобы выбрать очиститель воздуха\n"
            f"и оформить аренду:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🛒 Перейти в каталог", web_app=WebAppInfo(url=f"{WEBSITE}/shop.html"))]
                ]
            ),
        )
        return

    if deep == "calc_result":
        await message.answer(
            f"📊 <b>Калькулятор экономии</b>\n\n"
            f"Рассчитайте, сколько вы сэкономите с очистителем воздуха EcoAeris:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Открыть калькулятор", web_app=WebAppInfo(url=f"{WEBSITE}/calculator.html"))]
                ]
            ),
        )
        return

    if deep == "contact":
        await message.answer(
            f"📞 <b>Свяжитесь с нами</b>\n\n"
            f"Мы всегда рады помочь! Напишите нам через форму на сайте\n"
            f"или свяжитесь напрямую:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="📞 Контакты", web_app=WebAppInfo(url=f"{WEBSITE}/contact.html"))]
                ]
            ),
        )
        return

    # Deep links for tariff plans
    tariff_map = {
        "rent_basic": ("Basic", "Базовый тариф — идеально для дома и небольшого офиса."),
        "rent_business": ("Business", "Бизнес тариф — для среднего офиса и коммерческих помещений."),
        "rent_enterprise": ("Enterprise", "Корпоративный тариф — полное покрытие для крупных объектов."),
    }
    if deep in tariff_map:
        name, desc = tariff_map[deep]
        await message.answer(
            f"🏷 <b>Тариф {name}</b>\n\n"
            f"{desc}\n\n"
            f"Узнайте подробности и оформите аренду на нашем сайте:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=f"📋 Подробнее о {name}", web_app=WebAppInfo(url=f"{WEBSITE}/pricing.html"))]
                ]
            ),
        )
        return

    # Default /start
    await message.answer(
        f"👋 <b>Добро пожаловать в EcoAeris!</b>\n\n"
        f"🌿 Мы помогаем следить за качеством воздуха\n"
        f"и предлагаем аренду профессиональных очистителей.\n\n"
        f"<b>Что умеет этот бот:</b>\n"
        f"🌍 Проверить качество воздуха в любом городе\n"
        f"🛒 Просмотреть каталог очистителей\n"
        f"📊 Рассчитать экономию\n"
        f"ℹ️ Узнать о компании\n\n"
        f"Выберите действие 👇",
        reply_markup=main_keyboard(),
    )


# ──────────────────────────────────────────────
#  /help
# ──────────────────────────────────────────────
@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        f"📖 <b>Список команд:</b>\n\n"
        f"/start — Главное меню\n"
        f"/aqi — Проверить AQI (пример: /aqi tashkent)\n"
        f"/help — Показать это сообщение\n\n"
        f"Также вы можете просто отправить название города,\n"
        f"и бот покажет качество воздуха для него.",
        reply_markup=main_keyboard(),
    )


# ──────────────────────────────────────────────
#  /aqi [city]
# ──────────────────────────────────────────────
@router.message(Command("aqi"))
async def cmd_aqi(message: Message, command: CommandObject):
    city = command.args
    if not city:
        waiting_for_city.add(message.from_user.id)
        await message.answer(
            "🌍 <b>Введите название города</b>\n\n"
            "Например: <code>tashkent</code>, <code>moscow</code>, <code>london</code>"
        )
        return

    loading = await message.answer("⏳ Загрузка данных...")
    data = await fetch_aqi(city.strip())
    if data:
        await loading.edit_text(format_aqi_message(data))
    else:
        await loading.edit_text(
            f"❌ <b>Город «{city}» не найден</b>\n\n"
            f"Попробуйте ввести название на английском языке.\n"
            f"Пример: <code>tashkent</code>"
        )


# ──────────────────────────────────────────────
#  Callback handlers
# ──────────────────────────────────────────────
@router.callback_query(F.data == "aqi")
async def cb_aqi(callback: CallbackQuery):
    waiting_for_city.add(callback.from_user.id)
    await callback.message.answer(
        "🌍 <b>Введите название города</b>\n\n"
        "Например: <code>tashkent</code>, <code>moscow</code>, <code>london</code>"
    )
    await callback.answer()


@router.callback_query(F.data == "catalog")
async def cb_catalog(callback: CallbackQuery):
    await callback.message.answer(
        f"🛒 <b>Каталог очистителей воздуха</b>\n\n"
        f"Выберите подходящий очиститель и оформите аренду\n"
        f"прямо на нашем сайте:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🛒 Открыть каталог", web_app=WebAppInfo(url=f"{WEBSITE}/shop.html"))],
                [InlineKeyboardButton(text="🏷 Тарифы и цены", web_app=WebAppInfo(url=f"{WEBSITE}/pricing.html"))],
                [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="menu")],
            ]
        ),
    )
    await callback.answer()


@router.callback_query(F.data == "calculator")
async def cb_calculator(callback: CallbackQuery):
    await callback.message.answer(
        f"📊 <b>Калькулятор экономии</b>\n\n"
        f"Узнайте, сколько вы сэкономите, используя\n"
        f"очиститель воздуха EcoAeris:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📊 Открыть калькулятор", web_app=WebAppInfo(url=f"{WEBSITE}/calculator.html"))],
                [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="menu")],
            ]
        ),
    )
    await callback.answer()


@router.callback_query(F.data == "about")
async def cb_about(callback: CallbackQuery):
    await callback.message.answer(
        f"ℹ️ <b>О компании EcoAeris</b>\n\n"
        f"🌿 <b>EcoAeris</b> — сервис мониторинга качества воздуха\n"
        f"и аренды профессиональных очистителей.\n\n"
        f"✅ Мониторинг AQI в реальном времени\n"
        f"✅ Аренда очистителей для дома и офиса\n"
        f"✅ Гибкие тарифные планы\n"
        f"✅ Профессиональное обслуживание\n\n"
        f"Узнайте больше на нашем сайте:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🌐 О нас", web_app=WebAppInfo(url=f"{WEBSITE}/about.html"))],
                [InlineKeyboardButton(text="📞 Контакты", web_app=WebAppInfo(url=f"{WEBSITE}/contact.html"))],
                [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="menu")],
            ]
        ),
    )
    await callback.answer()


@router.callback_query(F.data == "menu")
async def cb_menu(callback: CallbackQuery):
    await callback.message.answer(
        "🏠 <b>Главное меню</b>\n\nВыберите действие 👇",
        reply_markup=main_keyboard(),
    )
    await callback.answer()


# ──────────────────────────────────────────────
#  Fallback: treat any text as city name for AQI
# ──────────────────────────────────────────────
@router.message(F.text)
async def handle_text(message: Message):
    text = message.text.strip()

    # Ignore messages that look like commands
    if text.startswith("/"):
        await message.answer(
            "❓ Неизвестная команда. Введите /help для списка команд."
        )
        return

    # If user was asked for a city or just sends a city name — try AQI
    user_id = message.from_user.id
    was_waiting = user_id in waiting_for_city
    waiting_for_city.discard(user_id)

    loading = await message.answer("⏳ Ищу данные о качестве воздуха...")
    data = await fetch_aqi(text)

    if data:
        await loading.edit_text(format_aqi_message(data))
    elif was_waiting:
        await loading.edit_text(
            f"❌ <b>Город «{text}» не найден</b>\n\n"
            f"Попробуйте ввести название на английском языке.\n"
            f"Пример: <code>tashkent</code>"
        )
    else:
        await loading.edit_text(
            f"🤔 Не удалось найти данные для «{text}».\n\n"
            f"Если вы хотели проверить AQI, введите /aqi или нажмите кнопку\n"
            f"«🌍 Проверить AQI» в меню.\n\n"
            f"Для списка команд: /help",
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
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("🚀 EcoAeris Bot started")

    # Set bot commands for the menu button
    from aiogram.types import BotCommand
    await bot.set_my_commands([
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="aqi", description="Проверить качество воздуха"),
        BotCommand(command="help", description="Помощь"),
    ])

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
