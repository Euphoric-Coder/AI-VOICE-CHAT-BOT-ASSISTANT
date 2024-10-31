import sys
from translate import Translator
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import speech_recognition as spr
from gtts import gTTS
import platform
import os


def translate_text(text, to_lang):
    translator = Translator(to_lang=to_lang)
    translation = translator.translate(text)
    return translation


class TranslatorApp(QDialog):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.load_stylesheets()

        self.theme_check_timer = QTimer(self)
        self.theme_check_timer.timeout.connect(self.check_and_update_theme)
        self.theme_check_timer.start(600)

    def initUI(self):
        self.setWindowTitle("Translator App")
        self.setGeometry(100, 100, 600, 400)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.label = QLabel("Enter text to translate or click 'Speak' to record voice")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.label)

        toolbar = QToolBar("Toolbar")
        main_layout.addWidget(toolbar)

        input_layout = QHBoxLayout()
        self.text_input = QLineEdit(self)
        input_layout.addWidget(self.text_input)


        translate_icon = QIcon("UI-IMAGES/translate.png")
        self.translate_button = QPushButton("Translate", self)
        self.translate_button.setIcon(translate_icon)
        self.translate_button.setIconSize(QSize(48, 48))
        self.translate_button.clicked.connect(self.translate_text)
        input_layout.addWidget(self.translate_button)

        speak_icon = QIcon("UI-IMAGES/microphone.png")
        self.speak_button = QPushButton("Speak", self)
        self.speak_button.setIcon(speak_icon)
        self.speak_button.setIconSize(QSize(48, 48))
        self.speak_button.clicked.connect(self.speak_text)
        input_layout.addWidget(self.speak_button)

        main_layout.addLayout(input_layout)

        self.language_selector = QComboBox(self)
        self.language_selector.addItems(
            [
                "Afrikaans (af)",
                "Arabic (ar)",
                "Bengali (bn)",
                "Chinese (zh)",
                "Czech (cs)",
                "Danish (da)",
                "Dutch (nl)",
                "English (en)",
                "Finnish (fi)",
                "French (fr)",
                "German (de)",
                "Greek (el)",
                "Gujarati (gu)",
                "Hebrew (he)",
                "Hindi (hi)",
                "Hungarian (hu)",
                "Indonesian (id)",
                "Italian (it)",
                "Japanese (ja)",
                "Kannada (kn)",
                "Korean (ko)",
                "Malay (ms)",
                "Marathi (mr)",
                "Nepali (ne)",
                "Norwegian (no)",
                "Polish (pl)",
                "Portuguese (pt)",
                "Punjabi (pa)",
                "Russian (ru)",
                "Spanish (es)",
                "Swedish (sv)",
                "Tamil (ta)",
                "Telugu (te)",
                "Thai (th)",
                "Turkish (tr)",
                "Ukrainian (uk)",
                "Urdu (ur)",
                "Vietnamese (vi)",
            ]
        )
        main_layout.addWidget(self.language_selector)

        self.translated_text = QTextEdit(self)
        self.translated_text.setReadOnly(True)
        main_layout.addWidget(self.translated_text)

        self.speak_timer = QTimer(self)
        self.speak_timer.timeout.connect(self.update_label_for_speak)
        self.speak_timer.setSingleShot(True)
        self.speak_countdown = 3

    def translate_text(self):
        text = self.text_input.text()
        if text:
            to_lang = self.get_selected_language()
            translated_text = translate_text(text, to_lang)
            self.translated_text.setPlainText(translated_text)
            self.speak_translated_text(translated_text)
            self.label.setText(
                "Enter text to translate or click 'Speak' to record voice"
            )
        else:
            self.translated_text.setPlainText(
                "Please enter text or use the 'Speak' button"
            )

    def speak_text(self):
        self.speak_countdown = 3
        self.label.setText(f"Speak now in {self.speak_countdown} seconds...")
        self.speak_timer.start(1000)

    def update_label_for_speak(self):
        self.speak_countdown -= 1
        if self.speak_countdown > 0:
            self.label.setText(f"Speak now in {self.speak_countdown} seconds...")
            self.speak_timer.start(1000)
        else:
            self.label.setText("Speak now...")
            QTimer.singleShot(1000, self.start_microphone)

    def start_microphone(self):
        recog1 = spr.Recognizer()
        mc = spr.Microphone()

        with mc as source:
            recog1.adjust_for_ambient_noise(source, duration=0.2)
            try:
                audio = recog1.listen(source, timeout=5, phrase_time_limit=10)
                MyText = recog1.recognize_google(audio)
                MyText = MyText.lower()
                self.text_input.setText(MyText)
                to_lang = self.get_selected_language()
                translated_text = translate_text(MyText, to_lang)
                self.translated_text.setPlainText(translated_text)
                self.speak_translated_text(translated_text)
                self.label.setText(
                    "Enter text to translate or click 'Speak' to record voice"
                )
            except spr.WaitTimeoutError:
                self.label.setText(
                    "Listening timed out while waiting for phrase to start"
                )
            except spr.UnknownValueError:
                self.label.setText("Unable to Understand the Input")
            except spr.RequestError as e:
                self.label.setText(f"Unable to provide Required Output: {e}")

    def speak_translated_text(self, text):
        to_lang = self.get_selected_language()
        try:
            speak = gTTS(text=text, lang=to_lang, slow=False)
            speak.save("captured_voice.mp3")
            self.play_audio("captured_voice.mp3")
        except Exception as e:
            self.translated_text.setPlainText(f"Speech error: {e}")

    def play_audio(self, file_path):
        if platform.system() == "Windows":
            os.system(f"start {file_path}")
        elif platform.system() == "Darwin":
            os.system(f"open {file_path}")
        else:
            os.system(f"xdg-open {file_path}")

    def get_selected_language(self):
        selected_lang = self.language_selector.currentText()
        return selected_lang.split(" ")[-1].strip("()")

    def load_stylesheet(self, path):
        style_sheet = ""
        with open(path, "r") as file:
            style_sheet = file.read()
        self.setStyleSheet(style_sheet)

    def load_stylesheets(self):
        if self.is_dark_mode():
            self.load_stylesheet("DarkUI.css")
        else:
            self.load_stylesheet("LightUI.css")

    def is_dark_mode(self):
        # Detect dark mode (placeholder for actual dark mode detection logic)
        return False

    def check_and_update_theme(self):
        if self.is_dark_mode():
            self.load_stylesheet("DarkUI.css")
        else:
            self.load_stylesheet("LightUI.css")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranslatorApp()
    window.show()
    sys.exit(app.exec())
