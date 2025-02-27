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
one_time_message = None  # буде зберігати об'єкт запущеного завдання

async def check_orders(message: Message, lang: str):
    global one_time_message
    while one_time_message:  # цикл працює поки активний
        scraper = cloudscraper.create_scraper()
        data = collect_orders(scraper)

        if data:
            if lang == 'Українською мовою':
                data = translate_message(data)

            for item in data:
                card = f"{item['Name']}\n  {item['Fixed_price']}\n  {item['Url']}\n   {item['Task']}\n  {item['Skills_Expertise']}\n"
                await message.answer(card)
        else:
            print(f"нових заказів немає ")

        await asyncio.sleep(200)

@dp.message(Command("start"))
async def start_command(message: Message):
    global one_time_message

    start_buttons = ['Українською мовою', 'in English']
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=button) for button in start_buttons]],
        resize_keyboard=True
    )
    if int(os.getenv("my_chat_id", 0)) == message.chat.id:
        if one_time_message:
            one_time_message.cancel()  # Зупиняємо попередній процес
        one_time_message = None  # Скидаємо значення

        Rewrite_order()
        await message.answer("Бот запущено", reply_markup=keyboard)
    else:
        await message.answer("This bot is created for personal use.", reply_markup=keyboard)

@dp.message()
async def handle_text(message: Message):
    global one_time_message
    if int(os.getenv("my_chat_id", 0)) == message.chat.id:
        if message.text in ['Українською мовою', 'in English']:
            if one_time_message:  # Якщо є активний цикл, зупиняємо його
                one_time_message.cancel()
            one_time_message = asyncio.create_task(check_orders(message, message.text))  # Створюємо новий цикл
    else:
        await message.answer("This bot is not for you")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())