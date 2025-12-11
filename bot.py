import asyncio
import logging
import requests
import sqlite3

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# Твої токени
API_TOKEN = "8419886191:AAFrzJZuHGOMsa41mGOvpDkzbJnUFGjvG7M"
RAWG_API_KEY = "78965f8bb8784ff5813c8e065a3d43b3"

# Логування
logging.basicConfig(level=logging.INFO)

# Ініціалізація
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# -------------------------------
# База даних SQLite
# -------------------------------
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    platform TEXT
)""")
conn.commit()

# -------------------------------
# Команди
# -------------------------------
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привіт 🎮! Я бот для підбору PlayStation ігор.")

@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer("Команди:\n/start\n/help\n/info\n/menu\n/choose\n/games\n/save")

@dp.message(Command("info"))
async def info_command(message: types.Message):
    await message.answer("Я використовую RAWG API, щоб показати популярні ігри для PlayStation.")

# -------------------------------
# Обробка тексту та фото
# -------------------------------
@dp.message(F.text)
async def echo_message(message: types.Message):
    await message.answer(f"Ти написав: {message.text}")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.answer("Фото отримав, але я працюю з іграми 😉")

# -------------------------------
# ReplyKeyboard (правильний синтаксис для 3.x)
# -------------------------------
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Топ ігри PS5")],
        [KeyboardButton(text="Топ ігри PS4")]
    ],
    resize_keyboard=True
)

@dp.message(Command("menu"))
async def show_menu(message: types.Message):
    await message.answer("Оберіть дію:", reply_markup=menu)

# -------------------------------
# InlineKeyboard (правильний синтаксис для 3.x)
# -------------------------------
inline_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="PS5", callback_data="ps5")],
        [InlineKeyboardButton(text="PS4", callback_data="ps4")]
    ]
)

@dp.message(Command("choose"))
async def choose_console(message: types.Message):
    await message.answer("Оберіть приставку:", reply_markup=inline_menu)

@dp.callback_query(F.data.in_(["ps5", "ps4"]))
async def process_callback(callback_query: types.CallbackQuery):
    if callback_query.data == "ps5":
        await callback_query.message.answer("Ви обрали PlayStation 5 ✅")
    else:
        await callback_query.message.answer("Ви обрали PlayStation 4 ✅")

# -------------------------------
# RAWG API інтеграція
# -------------------------------
def get_top_games(platform_id: int, count: int = 5):
    url = "https://api.rawg.io/api/games"
    params = {
        "key": RAWG_API_KEY,
        "platforms": platform_id,  # 18 = PS4, 187 = PS5
        "page_size": count
    }
    response = requests.get(url, params=params).json()
    return response.get("results", [])

@dp.message(Command("games"))
async def get_games(message: types.Message):
    games = get_top_games(187, 5)  # PS5
    if not games:
        await message.answer("Не вдалося отримати список ігор 😞")
        return
    reply = "🎮 Топ ігор для PlayStation 5:\n"
    for g in games:
        reply += f"- {g['name']} (рейтинг: {g.get('rating', 'N/A')})\n"
    await message.answer(reply)

# -------------------------------
# Збереження у базу
# -------------------------------
@dp.message(Command("save"))
async def save_user(message: types.Message):
    cursor.execute("INSERT INTO users (username, platform) VALUES (?, ?)",
                   (message.from_user.username, "PS5"))
    conn.commit()
    await message.answer("Ваш вибір збережено ✅")

# -------------------------------
# Запуск бота
# -------------------------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())