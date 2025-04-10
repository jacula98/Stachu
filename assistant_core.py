import json
import os
from datetime import datetime
from intent_parser import recognize_intent

# Pliki danych
SHOPPING_FILE = "shopping_list.txt"
REMINDERS_FILE = "reminders.json"

# -------------------------------
# Akcje
# -------------------------------

def add_to_shopping(item):
    with open(SHOPPING_FILE, "a", encoding="utf-8") as f:
        f.write(item + "\n")
    print(f"✅ Dodano do listy zakupowej: {item}")

def show_shopping():
    if not os.path.exists(SHOPPING_FILE):
        print("🛒 Lista zakupów jest pusta.")
        return
    with open(SHOPPING_FILE, "r", encoding="utf-8") as f:
        items = f.readlines()
    print("🛒 Lista zakupów:")
    for item in items:
        print(f"- {item.strip()}")

def remove_from_shopping(item):
    if not os.path.exists(SHOPPING_FILE):
        print("🛒 Lista jest już pusta.")
        return
    with open(SHOPPING_FILE, "r", encoding="utf-8") as f:
        items = [line.strip() for line in f.readlines()]
    if item in items:
        items.remove(item)
        with open(SHOPPING_FILE, "w", encoding="utf-8") as f:
            for i in items:
                f.write(i + "\n")
        print(f"❌ Usunięto z listy zakupowej: {item}")
    else:
        print(f"⚠️ Nie znaleziono na liście: {item}")

def add_reminder(text):
    now = datetime.now().isoformat()
    reminder = {"text": text, "timestamp": now}
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
            reminders = json.load(f)
    else:
        reminders = []
    reminders.append(reminder)
    with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(reminders, f, indent=2, ensure_ascii=False)
    print(f"🔔 Przypomnienie dodane: {text}")

def show_reminders():
    if not os.path.exists(REMINDERS_FILE):
        print("🔕 Brak przypomnień.")
        return
    with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
        reminders = json.load(f)
    print("📅 Przypomnienia:")
    for r in reminders:
        print(f"- {r['text']} ({r['timestamp']})")

# -------------------------------
# Główna pętla
# -------------------------------

if __name__ == "__main__":
    print("🎙️ Asystent gotowy. Wpisuj zdania (lub 'exit' by wyjść):\n")

    while True:
        user_input = input("Ty: ")
        if user_input.lower() in ["exit", "quit", "wyjdź"]:
            break

        intent, score = recognize_intent(user_input)
        print(f"🔍 Intencja: {intent} (dopasowanie: {round(score * 100)}%)")

        # Akcje na podstawie intencji
        if intent == "add_shopping":
            add_to_shopping(user_input)
        elif intent == "remove_shopping":
            remove_from_shopping(user_input)
        elif intent == "show_shopping":
            show_shopping()
        elif intent == "add_reminder":
            add_reminder(user_input)
        elif intent == "show_reminders":
            show_reminders()
        else:
            print("🤷‍♂️ Nie wiem jeszcze jak na to odpowiedzieć.")