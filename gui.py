import sys
import whisper
import sounddevice as sd
import queue
import tempfile
import numpy as np
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QTabWidget, QListWidget, QLabel, QMessageBox
)
from PySide6.QtCore import Qt

from assistant_core import add_to_shopping, remove_from_shopping, show_shopping, add_reminder, show_reminders
from intent_parser import recognize_intent
import soundfile as sf

model = whisper.load_model("base")
samplerate = 16000
duration = 4
q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(indata.copy())

def record_audio():
    with sd.InputStream(samplerate=samplerate, channels=1, callback=callback):
        audio = []
        import time
        start = time.time()
        while time.time() - start < duration:
            audio.extend(q.get())
        return np.concatenate(audio, axis=0)

def save_temp_wav(audio_data):
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(temp_file.name, audio_data, samplerate, subtype='PCM_16')
    return temp_file.name

class VoiceAssistantApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asystent Głosowy")
        self.setGeometry(100, 100, 400, 500)

        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Tab: Nagrywanie
        self.record_tab = QWidget()
        self.record_layout = QVBoxLayout()
        self.record_button = QPushButton("🎙️ Nagraj")
        self.record_button.clicked.connect(self.handle_record)
        self.recognized_text = QLabel("Tutaj pojawi się rozpoznany tekst.")
        self.record_layout.addWidget(self.record_button)
        self.record_layout.addWidget(self.recognized_text)
        self.record_tab.setLayout(self.record_layout)

        # Tab: Zakupy
        self.shopping_tab = QWidget()
        self.shopping_layout = QVBoxLayout()
        self.shopping_list = QListWidget()
        self.shopping_layout.addWidget(self.shopping_list)
        self.shopping_tab.setLayout(self.shopping_layout)

        # Tab: Przypomnienia
        self.reminders_tab = QWidget()
        self.reminders_layout = QVBoxLayout()
        self.reminders_list = QListWidget()
        self.reminders_layout.addWidget(self.reminders_list)
        self.reminders_tab.setLayout(self.reminders_layout)

        self.tabs.addTab(self.record_tab, "🎤 Nagrywanie")
        self.tabs.addTab(self.shopping_tab, "🛒 Zakupy")
        self.tabs.addTab(self.reminders_tab, "⏰ Przypomnienia")

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.refresh_lists()

    def handle_record(self):
        self.recognized_text.setText("⏳ Rozpoznaję głos...")
        QApplication.processEvents()

        try:
            audio = record_audio()
            wav_path = save_temp_wav(audio)
            result = model.transcribe(wav_path, language="pl")
            os.remove(wav_path)
            text = result["text"].strip()
            self.recognized_text.setText(f"🗣️ Rozpoznano: \"{text}\"")

            intent, score = recognize_intent(text)

            if intent == "add_shopping":
                add_to_shopping(text)
            elif intent == "remove_shopping":
                remove_from_shopping(text)
            elif intent == "show_shopping":
                pass
            elif intent == "add_reminder":
                add_reminder(text)
            elif intent == "show_reminders":
                pass
            else:
                QMessageBox.information(self, "🤔", "Nie wiem jeszcze jak zareagować na to zdanie.")

            self.refresh_lists()

        except Exception as e:
            self.recognized_text.setText("❌ Błąd rozpoznawania")
            QMessageBox.critical(self, "Błąd", str(e))

    def refresh_lists(self):
        self.shopping_list.clear()
        for item in show_shopping(return_list=True):
            self.shopping_list.addItem(f"• {item}")

        self.reminders_list.clear()
        for item in show_reminders(return_list=True):
            self.reminders_list.addItem(f"• {item}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoiceAssistantApp()
    window.show()
    sys.exit(app.exec())
