import asyncio
import logging
import aiosqlite
import requests

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# ==============================
# 🔐 CONFIG
# ==============================
API_TOKEN = "8419886191:AAFrzJZuHGOMsa41mGOvpDkzbJnUFGjvG7M"
RAWG_API_KEY = "78965f8bb8784ff5813c8e065a3d43b3"

# ==============================
# LOGGING
# ==============================
logging.basicConfig(level=logging.INFO)


# ==============================
# 📌 ІНІЦІАЛІЗАЦІЯ БОТА
# ==============================
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# ==============================
# 📂 АСИНХРОННА БАЗА ДАНИХ (SQLite)
# ==============================
async def init_db():
    async with aiosqlite.connect("users.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                platform TEXT
            )
        """)
        await db.commit()


async def save_user(username: str, platform: str = "PS5"):
    async with aiosqlite.connect("users.db") as db:
        await db.execute("""
            INSERT OR REPLACE INTO users (username, platform)
            VALUES (?, ?)
        """, (username, platform))
        await db.commit()


# ==============================
# 🎮 RAWG API
# ==============================
def get_top_games(platform_id: int, count: int = 5):
    url = "https://api.rawg.io/api/games"
    params = {
        "key": RAWG_API_KEY,
        "platforms": platform_id,
        "ordering": "-rating",
        "page_size": count,
    }

    r = requests.get(url, params=params).json()
    return r.get("results", [])


# ==============================
# 🧩 КЛАВІАТУРИ
# ==============================
reply_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Топ ігри PS5")],
        [KeyboardButton(text="Топ ігри PS4")]
    ],
    resize_keyboard=True
)

inline_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="PS5", callback_data="ps5")],
        [InlineKeyboardButton(text="PS4", callback_data="ps4")]
    ]
)


# ==============================
# 🧵 ХЕНДЛЕРИ
# ==============================

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привіт 🎮! Я допоможу підібрати ігри для PlayStation.\nВикористай /menu")


@dp.message(Command("menu"))
async def menu(message: types.Message):
    await message.answer("Оберіть дію:", reply_markup=reply_menu)


@dp.message(F.text == "Топ ігри PS5")
async def top_ps5(message: types.Message):
    await send_games(message, platform_id=187, title="PlayStation 5")


@dp.message(F.text == "Топ ігри PS4")
async def top_ps4(message: types.Message):
    await send_games(message, platform_id=18, title="PlayStation 4")


@dp.message(Command("choose"))
async def choose(message: types.Message):
    await message.answer("Оберіть приставку:", reply_markup=inline_menu)


@dp.callback_query(F.data.in_(["ps5", "ps4"]))
async def callback_console(call: types.CallbackQuery):
    platform = call.data.upper()
    await call.message.answer(f"Ви обрали {platform} ✅")


async def send_games(message: types.Message, platform_id: int, title: str):
    games = get_top_games(platform_id)

    if not games:
        await message.answer("Не вдалося отримати список ігор 😞")
        return

    text = f"🎮 Топ ігор для {title}:\n\n"
    for g in games:
        text += f"• {g['name']} (рейтинг: {g.get('rating', 'N/A')})\n"

    await message.answer(text)


@dp.message(Command("save"))
async def save(message: types.Message):
    await save_user(message.from_user.username)
    await message.answer("Ваш вибір збережено у базу даних ✅")


# ==============================
# 🚀 ЗАПУСК
# ==============================
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
