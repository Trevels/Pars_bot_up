from Pars import collect_orders, Rewrite_order, translate_message
import cloudscraper
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
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
                Name = item["Name"]
                Fixed_price = item["Fixed_price"]
                Task = item["Task"]
                Skills_Expertise = item["Skills_Expertise"]
                Url = item["Url"]

                # Формуємо текст без прямого посилання
                card_text = (
                    f"🔔 Новий фріланс-проєкт!\n\n"
                    f"📌 {Name}\n"
                    f"💰 {Fixed_price}\n"
                    f"📝 {Task}\n"
                    f"🎯 {Skills_Expertise}\n\n"
                    f"🌍 Перегляньте деталі за посиланням:"
                )

                # Додаємо кнопку "Переглянути"
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="🔗 Переглянути", callback_data=f"view_{Url}")]
                    ]
                )

                await message.answer(card_text, reply_markup=keyboard)
        else:
            print(f"Нових замовлень немає для {chat_id}")

        await asyncio.sleep(200)  # Чекаємо 200 секунд перед новою перевіркою

@dp.callback_query()
async def handle_callback(callback_query: types.CallbackQuery):
    """ Обробляє натискання на кнопку "Переглянути" і надсилає посилання приватно """
    callback_data = callback_query.data

    if callback_data.startswith("view_"):
        url = callback_data.replace("view_", "")
        await callback_query.message.answer(f"🔗 Ось ваше посилання: {url}")
        await callback_query.answer()  # Закриваємо повідомлення про натискання

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