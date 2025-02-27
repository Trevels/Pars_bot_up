from Pars import collect_orders, Rewrite_order, translate_message
import cloudscraper
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
import asyncio

load_dotenv()

bot = Bot(token=os.getenv("token"))
dp = Dispatcher()
active_tasks = {}  # Замість глобальної змінної, зберігаємо запущені цикли для кожного користувача

async def check_orders(message: Message, lang: str):
    chat_id = message.chat.id
    while chat_id in active_tasks:  # Якщо користувач не відключився
        scraper = cloudscraper.create_scraper()
        data = collect_orders(scraper)

        if data:
            if lang == 'Українською мовою':
                data = translate_message(data)

            for item in data:
                card = f"{item['Name']}\n  {item['Fixed_price']}\n  {item['Url']}\n   {item['Task']}\n  {item['Skills_Expertise']}\n"
                await message.answer(card)
        else:
            print(f"нових заказів немає для {chat_id}")

        await asyncio.sleep(200)  # Чекаємо 200 секунд перед новою перевіркою

@dp.message(Command("start"))
async def start_command(message: Message):
    chat_id = message.chat.id

    start_buttons = ['Українською мовою', 'in English']
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=button) for button in start_buttons]],
        resize_keyboard=True
    )

    # Якщо вже запущено завдання для цього користувача, зупиняємо його
    if chat_id in active_tasks:
        active_tasks[chat_id].cancel()
        del active_tasks[chat_id]

    Rewrite_order()
    await message.answer("Бот запущено", reply_markup=keyboard)

@dp.message()
async def handle_text(message: Message):
    chat_id = message.chat.id

    if message.text in ['Українською мовою', 'in English']:
        # Якщо є активний цикл для цього користувача, зупиняємо його
        if chat_id in active_tasks:
            active_tasks[chat_id].cancel()
            del active_tasks[chat_id]

        # Створюємо нове завдання для конкретного користувача
        active_tasks[chat_id] = asyncio.create_task(check_orders(message, message.text))

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())