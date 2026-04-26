# EcoAeris Telegram Bot

Telegram-бот для мониторинга качества воздуха и навигации по сервису EcoAeris.

## Возможности

- Проверка AQI (индекса качества воздуха) для любого города
- Каталог очистителей воздуха
- Калькулятор экономии
- Информация о компании
- Deep-link поддержка для интеграции с сайтом

## Установка и запуск

### 1. Создайте виртуальное окружение (рекомендуется)

```bash
cd bot
python -m venv venv
source venv/bin/activate   # macOS / Linux
# venv\Scripts\activate    # Windows
```

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

### 3. Запустите бота

```bash
python main.py
```

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Главное меню |
| `/aqi` | Проверить AQI (например: `/aqi tashkent`) |
| `/help` | Список команд |

## Deep Links

Бот поддерживает deep links для интеграции с сайтом:

- `t.me/bot?start=website` — открыть сайт
- `t.me/bot?start=order` — перейти к заказу
- `t.me/bot?start=calc_result` — калькулятор экономии
- `t.me/bot?start=contact` — контакты
- `t.me/bot?start=rent_basic` — тариф Basic
- `t.me/bot?start=rent_business` — тариф Business
- `t.me/bot?start=rent_enterprise` — тариф Enterprise

## Технологии

- Python 3.10+
- aiogram 3.x
- WAQI API для данных о качестве воздуха
