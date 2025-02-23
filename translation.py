import json
from deep_translator import GoogleTranslator

# Функція для перекладу тексту
def translate_text(text, target_language="uk"):
    return GoogleTranslator(source="auto", target=target_language).translate(text)

def translate_message():
    # Відкриваємо JSON
    with open("new_orders.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    # Перекладаємо необхідні поля
    for item in data:
        item["Name"] = translate_text(item["Name"])
        item["Task"] = translate_text(item["Task"])
        item["Skills_Expertise"] = translate_text(item["Skills_Expertise"])

    # Зберігаємо перекладений JSON
    with open("translated_data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print("Переклад завершено! ✅")
