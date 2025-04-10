# 📦 Główne zależności:
# pip install PySide6 openai-whisper sounddevice numpy pyttsx3 llama-index

import sys
import os
import tempfile
import threading
import sounddevice as sd
import numpy as np
import whisper
import json
import pyttsx3
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QLabel
from PySide6.QtCore import Qt, QTimer
from datetime import datetime
from scipy.io.wavfile import write
import random
from llama_index import SimpleDirectoryReader, VectorStoreIndex, ServiceContext
from llama_index.llms import OpenAI

# 🎙️ Ustawienia nagrywania
duration = 5  # sekund
samplerate = 16000

# 🔊 Ścieżki do plików
data_dir = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(data_dir, exist_ok=True)
shopping_file = os.path.join(data_dir, "shopping_list.json")
reminder_file = os.path.join(data_dir, "reminders.json")
docs_dir = os.path.join(data_dir, "documents")

# 🎧 Model Whisper (tiny dla szybkości)
model = whisper.load_model("tiny")

# 📋 Lista zakupów i przypomnień
shopping_list = []
reminders = []

# 🧠 Prosta baza wiedzy i dialogów
simple_responses = {
    "jak się masz": ["Mam się dobrze, dziękuję!", "Działam sprawnie!", "Wszystko pod kontrolą."],
    "co u ciebie": ["Cały czas czekam na Twoje polecenia!", "Gotowy do działania!"],
    "jaka jest dziś data": [datetime.now().strftime("Dziś jest %A, %d %B %Y")],
    "jaki jest dziś dzień tygodnia": [datetime.now().strftime("Dziś jest %A")],
    "dziękuję": ["Nie ma za co!", "Zawsze do usług."],
    "hej": ["Cześć! Jak mogę pomóc?", "Hejka!"],
    "czy jesteś tam": ["Tak, słucham Cię uważnie.", "Jestem tutaj, gotowy do pomocy."]
}

# 🔈 Inicjalizacja syntezatora mowy
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

# 📚 Inicjalizacja RAG (LlamaIndex)
service_context = ServiceContext.from_defaults(llm=OpenAI(temperature=0, model="gpt-3.5-turbo"))
documents = SimpleDirectoryReader(docs_dir).load_data()
index = VectorStoreIndex.from_documents(documents, service_context=service_context)
rag_engine = index.as_query_engine()

def load_data():
    global shopping_list, reminders
    try:
        if os.path.exists(shopping_file):
            with open(shopping_file, "r", encoding="utf-8") as f:
                shopping_list.extend(json.load(f))
        if os.path.exists(reminder_file):
            with open(reminder_file, "r", encoding="utf-8") as f:
                reminders.extend(json.load(f))
    except Exception as e:
        print(f"Błąd ładowania danych: {e}")

def save_data():
    try:
        with open(shopping_file, "w", encoding="utf-8") as f:
            json.dump(shopping_list, f, ensure_ascii=False, indent=2)
        with open(reminder_file, "w", encoding="utf-8") as f:
            json.dump(reminders, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Błąd zapisu danych: {e}")

class VoiceAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asystent Głosowy")
        self.setMinimumSize(400, 400)

        self.label = QLabel("Kliknij, aby mówić", alignment=Qt.AlignCenter)
        self.button = QPushButton("🎙️ Nagraj polecenie")
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        layout.addWidget(self.output)
        self.setLayout(layout)

        self.button.clicked.connect(self.start_recording)

        load_data()
        self.output.append("📥 Dane wczytane.")

        self.reminder_timer = QTimer()
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start(60000)  # co minutę

    def start_recording(self):
        self.label.setText("Nagrywanie...")
        self.button.setEnabled(False)
        thread = threading.Thread(target=self.record_and_transcribe)
        thread.start()

    def record_and_transcribe(self):
        audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()

        temp_wav = os.path.join(tempfile.gettempdir(), "temp.wav")
        write(temp_wav, samplerate, audio)

        result = model.transcribe(temp_wav, language="pl")
        text = result["text"].strip()

        self.output.append(f"🗣️ {text}")
        self.handle_command(text)

        self.label.setText("Kliknij, aby mówić")
        self.button.setEnabled(True)

    def handle_command(self, text):
        lowered = text.lower()
        if "dodaj do zakupów" in lowered:
            item = lowered.split("dodaj do zakupów")[-1].strip()
            if item:
                shopping_list.append(item)
                save_data()
                msg = f"🛒 Dodano do listy zakupów: {item}"
                self.output.append(msg)
                speak(msg)
        elif "usuń z zakupów" in lowered:
            item = lowered.split("usuń z zakupów")[-1].strip()
            if item in shopping_list:
                shopping_list.remove(item)
                save_data()
                msg = f"🗑️ Usunięto z listy zakupów: {item}"
                self.output.append(msg)
                speak(msg)
        elif "przypomnij mi o" in lowered:
            reminder = lowered.split("przypomnij mi o")[-1].strip()
            if reminder:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                reminders.append({"text": reminder, "added": timestamp})
                save_data()
                msg = f"⏰ Dodano przypomnienie: {reminder}"
                self.output.append(msg)
                speak(msg)
        elif "pokaż listę zakupów" in lowered:
            self.output.append("📋 Lista zakupów:")
            speak("Oto Twoja lista zakupów")
            for item in shopping_list:
                self.output.append(f"- {item}")
        elif "pokaż przypomnienia" in lowered:
            self.output.append("📌 Przypomnienia:")
            speak("Oto Twoje przypomnienia")
            for r in reminders:
                self.output.append(f"- {r['text']} (dodano {r['added']})")
        else:
            for key, responses in simple_responses.items():
                if key in lowered:
                    response = random.choice(responses)
                    self.output.append(f"💬 {response}")
                    speak(response)
                    return
            rag_response = rag_engine.query(text)
            msg = f"📚 {rag_response.response}"
            self.output.append(msg)
            speak(rag_response.response)

    def check_reminders(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        for r in reminders:
            if now in r['text']:
                self.output.append(f"🔔 Przypomnienie: {r['text']}")
                speak(f"Przypomnienie: {r['text']}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VoiceAssistant()
    window.show()
    sys.exit(app.exec())
