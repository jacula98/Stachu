from difflib import SequenceMatcher

# Intencje i przykłady
intent_examples = {
    "add_shopping": [
        "Dodaj mleko do listy zakupów",
        "Muszę kupić chleb",
        "Zapisz na liście zakupowej jajka",
        "Dorzuć ser do zakupów",
    ],
    "add_reminder": [
        "Przypomnij mi o urodzinach taty",
        "Dodaj przypomnienie na jutro: lekarz",
        "Muszę pamiętać o spotkaniu",
        "Zapamiętaj, że mam dentystę",
    ],
    "remove_shopping": [
        "Usuń mleko z listy",
        "Skreśl chleb z zakupów",
        "Już nie potrzebuję jajek",
    ],
    "show_reminders": [
        "Pokaż przypomnienia",
        "Jakie mam dziś zadania?",
        "Co mam zaplanowane?",
    ],
    "show_shopping": [
        "Pokaż listę zakupów",
        "Co mam kupić?",
    ],
}

def recognize_intent(user_input):
    best_intent = None
    best_score = 0.0

    for intent, examples in intent_examples.items():
        for example in examples:
            score = SequenceMatcher(None, user_input.lower(), example.lower()).ratio()
            if score > best_score:
                best_score = score
                best_intent = intent

    return best_intent, best_score

# Testy lokalne
if __name__ == "__main__":
    while True:
        user_input = input("Ty: ")
        if user_input.lower() in ["exit", "quit", "wyjdź"]:
            break
        intent, score = recognize_intent(user_input)
        print(f"Rozpoznana intencja: {intent} (dopasowanie: {round(score*100)}%)")
