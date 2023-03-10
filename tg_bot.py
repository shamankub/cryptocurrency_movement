import asyncio
import os

import ccxt.async_support as ccxt
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from dotenv import load_dotenv

from main import analyze_futures_prices

exchange = ccxt.binance()

# Загрузка переменных окружения из .env файла
load_dotenv()

# Создаём бота и диспетчера
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Определяем команду для запуска бота
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # Создаём клавиатуру с наиболее популярными торговыми парами
    global send_messages
    send_messages = True
    most_popular = ["ETH/USDT", "BNB/USDT", "ADA/USDT", "DOT/USDT", "XRP/USDT", "DOGE/USDT", "SOL/USDT", "LUNA/USDT", "UNI/USDT"]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for symbol in most_popular:
        button = types.InlineKeyboardButton(text=symbol, callback_data=symbol)
        keyboard.add(button)

    # Отправляем приветственное сообщение с помощью /start
    welcome_message = f"Привет, я крипто-бот.\nЯ слежу за ценой выбранного фьючерса и определяю собственные движения его цены. "\
                    f"При изменении цены на 1% за последние 60 минут, я буду присылать тебе сообщение.\n"\
                    f"Для справки введите команду /help"
    await message.reply(welcome_message, reply_markup=keyboard)


# Определяем функцию обратного вызова для нажатия кнопки
@dp.callback_query_handler(lambda c: True)
async def process_callback(callback_query: types.CallbackQuery):
    # Получаем название торговой пары от нажатия кнопки
    symbol = callback_query.data

    while send_messages:
        # Анализируем цены фьючерсов
        result = await analyze_futures_prices(symbol)
        if result:
            # Отправляем сообщение пользователю с результатом
            await bot.send_message(chat_id=callback_query.from_user.id, text=result)
            await asyncio.sleep(60)
        

# Определяем команду для остановки бота
@dp.message_handler(commands=['stop'])
async def send_stop(message: types.Message):
    global send_messages
    send_messages = False
    await message.reply("Отправка сообщений остановлена")


# Определяем команду /help
@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    help_text = "Доступны следующие команды:\n"
    help_text += "/start - Запустить бота\n"
    help_text += "/stop - Остановить бота\n"
    help_text += "/help - Показать справку\n"
    await message.reply(help_text)


async def schedule():
    while True:
        await asyncio.sleep(60)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
