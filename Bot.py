from Pars import collect_orders, Rewrite_order,translate_message
import cloudscraper

import os
from dotenv import load_dotenv
load_dotenv()

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message 
from aiogram.filters import Command
import asyncio


bot = Bot(token=os.getenv("token"))
dp = Dispatcher()
one_time_message = True#відповідає за вихід з циклу а також щоб неповторювався виклик одної і той самої дії(коли пишимо повідомлення) можуть виникати помилки врато змінити логіку зупинки циклу

@dp.message(Command("start"))
async def start_command(message: Message):
    global one_time_message

    start_buttons = ['Українською мовою', 'in English']
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=button) for button in start_buttons]],
        resize_keyboard=True
    )
    if int(os.getenv("my_chat_id", 0)) == message.chat.id:

        one_time_message = False
        Rewrite_order()
        await message.answer(f"Бот запущено",reply_markup=keyboard)
    else:
        await message.answer(f"This bot is created for personal use.",reply_markup=keyboard)


@dp.message()
async def handle_text(message: Message):
    global one_time_message
    if int(os.getenv("my_chat_id", 0)) == message.chat.id and not one_time_message:
        one_time_message = True#для того щоб цикел працював тільки по одному колу
        if message.text == 'Українською мовою' or message.text == 'in English':
            while one_time_message:
                scraper = cloudscraper.create_scraper()
                data = collect_orders(scraper)
                if data:
                    if message.text == 'Українською мовою':
                        data=translate_message(data)

                    for item in data:    
                        Name = item["Name"]
                        Fixed_price = item["Fixed_price"]
                        Url = item["Url"]
                        Task = item["Task"]
                        Skills_Expertise = item["Skills_Expertise"]

                        card = f"{Name}\n  {Fixed_price}\n  {Url}\n   {Task}\n  {Skills_Expertise}\n"
                        await message.answer(card)
                else:
                    print(f"нових заказів немає ")
                await asyncio.sleep(200)  
    else:
        await message.answer(f"This bot is not for you")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())