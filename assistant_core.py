# assistant_core.py

import json
import os

shopping_file = "shopping_list.json"
reminders_file = "reminders_list.json"

shopping_list = []
reminders_list = []

# -------------------- ZAPIS / ODCZYT --------------------

def load_data():
    global shopping_list, reminders_list
    if os.path.exists(shopping_file):
        with open(shopping_file, "r", encoding="utf-8") as f:
            shopping_list = json.load(f)
    if os.path.exists(reminders_file):
        with open(reminders_file, "r", encoding="utf-8") as f:
            reminders_list = json.load(f)

def save_data():
    with open(shopping_file, "w", encoding="utf-8") as f:
        json.dump(shopping_list, f, ensure_ascii=False, indent=2)
    with open(reminders_file, "w", encoding="utf-8") as f:
        json.dump(reminders_list, f, ensure_ascii=False, indent=2)

# -------------------- FUNKCJE LISTY ZAKUPÓW --------------------

def add_to_shopping(text):
    item = extract_item_from_text(text)
    if item:
        shopping_list.append(item)
        save_data()
        print(f"✅ Dodano do listy zakupów: {item}")
    else:
        print("⚠️ Nie rozpoznano, co dodać do listy zakupów.")

def remove_from_shopping(text):
    item = extract_item_from_text(text)
    if item in shopping_list:
        shopping_list.remove(item)
        save_data()
        print(f"🗑️ Usunięto z listy zakupów: {item}")
    else:
        print("⚠️ Nie znaleziono tego elementu na liście.")

def show_shopping(return_list=False):
    if return_list:
        return shopping_list
    print("🛒 Lista zakupów:")
    for item in shopping_list:
        print(f"- {item}")

# -------------------- FUNKCJE PRZYPOMNIEŃ --------------------

def add_reminder(text):
    reminders_list.append(text)
    save_data()
    print(f"⏰ Dodano przypomnienie: {text}")

def show_reminders(return_list=False):
    if return_list:
        return reminders_list
    print("📅 Przypomnienia:")
    for reminder in reminders_list:
        print(f"- {reminder}")

# -------------------- EKSTRAKCJA TEKSTU --------------------

def extract_item_from_text(text):
    words = text.lower().replace(",", "").split()
    if not words:
        return None

    ignore_words = {"dodaj", "do", "listy", "zakupów", "muszę", "kupić", "potrzebuję", "chcę", "wrzucam", "kupic"}
    item_words = [w for w in words if w not in ignore_words]
    return " ".join(item_words).strip() if item_words else None


# Wczytaj dane przy uruchomieniu
load_data()
