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

# 🎙️ Ustawienia nagrywania
duration = 5  # sekund
samplerate = 16000

# 🎧 Model Whisper (tiny dla szybkości)
model = whisper.load_model("tiny")

class VoiceAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asystent Głosowy")
        self.setMinimumSize(400, 300)

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
        text = result["text"]

        self.output.append(f"🗣️ {text}")
        self.label.setText("Kliknij, aby mówić")
        self.button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VoiceAssistant()
    window.show()
    sys.exit(app.exec())
