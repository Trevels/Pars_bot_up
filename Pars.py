import json
import cloudscraper
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

import os
from dotenv import load_dotenv
load_dotenv()
proxy = {
    'http': os.getenv('HTTP_PROXY'),
    'https': os.getenv('HTTPS_PROXY')
}


def collect_orders(scraper= cloudscraper.create_scraper()):
    response = scraper.get(token=os.getenv("url"),proxies=proxy)
    print("Response status:", response.status_code)

    new_orders = []
    
    try:#для постійной обробки працює некорктно мб try
        soup = BeautifulSoup(response.text, "html.parser")
        blook = soup.find('div', class_='span-12 span-lg-9')
        all_orders = blook.find_all("article", class_="job-tile cursor-pointer px-md-4 air3-card air3-card-list px-4x")

        # Завантажуємо раніше знайдені замовлення
        try:
            with open("all_orders.json", "r", encoding="utf-8") as f:
                existing_orders = json.load(f)
                if not isinstance(existing_orders, list):
                    existing_orders = []
        except (FileNotFoundError, json.JSONDecodeError):
            existing_orders = []

        existing_names = {order["Name"] for order in existing_orders}  # Множина для швидкої перевірки


        for orders in all_orders:
            Fixed_price = orders.find("ul").find("li", {"data-test": "job-type-label"}).text.strip()
            if Fixed_price == "Fixed price":
                Fixed_price = orders.find("ul").find("li", {"data-test": "is-fixed-price"}).text.strip()

            data = {
                'Name': orders.find_all("div", class_="air3-line-clamp is-clamped")[0].text,
                'Fixed_price': Fixed_price,
                'Url': f"https://www.upwork.com{orders.find_all('div', class_='air3-line-clamp is-clamped')[0].find('a').get('href')}",
                'Task': orders.find_all("div", class_="air3-line-clamp is-clamped")[1].text.strip(),
                'Skills_Expertise': orders.find("div", class_="air3-token-container").text if orders.find("div", class_="air3-token-container") else ""
            }

            if data["Name"] not in existing_names:  # Якщо замовлення нове
                new_orders.append(data)
                existing_orders.append(data)  # Додаємо його в загальний список

        # Якщо є нові замовлення → зберігаємо їх у файли
        if new_orders:

            with open("all_orders.json", "w", encoding="utf-8") as f:
                json.dump(existing_orders, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Erorr :{e}")
        print("Response text:", response.text[:2000])  # Виводимо 2000 символів HTML

    return new_orders  # Повертаємо нові замовлення (наприклад, для Telegram-бота)

def Rewrite_order():
    try:
    # Зчитуємо дані з файлу
        with open("all_orders.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # Переконуємось, що дані - це список
        if isinstance(data, list):
            last_10 = data[-10:]  # Беремо останні 10 елементів

            # Перезаписуємо файл
            with open("all_orders.json", "w", encoding="utf-8") as f:
                json.dump(last_10, f, indent=4, ensure_ascii=False)
        else:
            print("Помилка: JSON не є списком!")

    except Exception as e:
        print(f"Сталася помилка: {e}")

# Функція для перекладу тексту
def translate_message(data, target_language="uk"):
    translator = GoogleTranslator(source="auto", target=target_language)  # Створюємо об'єкт перекладача

    translated_list = []  # Список для збереження результату

    for item in data:

        translated_item = {
            "Name": translator.translate(item["Name"]),
            "Fixed_price": item["Fixed_price"],
            "Url": item["Url"],
            "Task": translator.translate(item["Task"]),
            "Skills_Expertise": translator.translate(item["Skills_Expertise"]),
        }

        translated_list.append(translated_item)  # Додаємо перекладений елемент у список

    print("Переклад завершено! ✅")
    return translated_list
  
