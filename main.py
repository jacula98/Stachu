# 📦 Główne zależności:
# pip install PySide6 openai-whisper sounddevice numpy

import sys
import os
import tempfile
import threading
import sounddevice as sd
import numpy as np
import whisper
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QLabel
from PySide6.QtCore import Qt
from datetime import datetime

# 🎙️ Ustawienia nagrywania
duration = 5  # sekund
samplerate = 16000

# 🎧 Model Whisper (tiny dla szybkości)
model = whisper.load_model("medium")

# 📋 Lista zakupów i przypomnień
shopping_list = []
reminders = []

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

    def start_recording(self):
        self.label.setText("Nagrywanie...")
        self.button.setEnabled(False)
        thread = threading.Thread(target=self.record_and_transcribe)
        thread.start()

    def record_and_transcribe(self):
        audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()

        # Zapisz tymczasowo
        temp_wav = os.path.join(tempfile.gettempdir(), "temp.wav")
        from scipy.io.wavfile import write
        write(temp_wav, samplerate, audio)

        # Transkrypcja
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
                self.output.append(f"🛒 Dodano do listy zakupów: {item}")
        elif "przypomnij mi o" in lowered:
            reminder = lowered.split("przypomnij mi o")[-1].strip()
            if reminder:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                reminders.append((reminder, timestamp))
                self.output.append(f"⏰ Dodano przypomnienie: {reminder}")
        elif "pokaż listę zakupów" in lowered:
            self.output.append("📋 Lista zakupów:")
            for item in shopping_list:
                self.output.append(f"- {item}")
        elif "pokaż przypomnienia" in lowered:
            self.output.append("📌 Przypomnienia:")
            for reminder, time in reminders:
                self.output.append(f"- {reminder} (dodano {time})")
        else:
            self.output.append("🤖 Nie rozumiem polecenia.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VoiceAssistant()
    window.show()
    sys.exit(app.exec())
