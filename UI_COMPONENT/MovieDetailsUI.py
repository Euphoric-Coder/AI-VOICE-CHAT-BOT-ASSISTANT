import sys
import imdb
from gtts import gTTS
import speech_recognition as sr
import datetime
import os
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


def speak(command):
    speech = gTTS(command)
    speech_file = "speech.mp3"
    speech.save(speech_file)
    os.system("afplay " + speech_file)  # For macOS
    # For Windows use: os.system("start " + speech_file)
    # For Linux use: os.system("xdg-open " + speech_file)


class MovieSearchApp(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_stylesheets()

        self.theme_check_timer = QTimer(self)
        self.theme_check_timer.timeout.connect(self.check_and_update_theme)
        self.theme_check_timer.start(600)

    def initUI(self):
        self.setWindowTitle("Movie Search App")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel("Enter movie name or click 'Speak' to record voice")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        input_layout = QHBoxLayout()
        self.text_input = QLineEdit(self)
        input_layout.addWidget(self.text_input)

        self.search_icon = QIcon("UI-IMAGES/movie-search.png")
        self.search_button = QPushButton("Search", self)
        self.search_button.setIcon(self.search_icon)
        self.search_button.setIconSize(QSize(48, 48))
        self.search_button.clicked.connect(self.search_movie)
        input_layout.addWidget(self.search_button)

        self.speak_icon = QIcon("UI-IMAGES/microphone.png")
        self.speak_button = QPushButton("Speak", self)
        self.speak_button.setIcon(self.speak_icon)
        self.speak_button.setIconSize(QSize(48, 48))
        self.speak_button.clicked.connect(self.speak_text)
        input_layout.addWidget(self.speak_button)

        layout.addLayout(input_layout)

        self.movie_details = QTextEdit(self)
        self.movie_details.setReadOnly(True)
        layout.addWidget(self.movie_details)

        self.speak_details_button = QPushButton("Speak Details", self)
        self.speak_details_button.clicked.connect(self.speak_movie_details)
        layout.addWidget(self.speak_details_button)

    def get_audio(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.pause_threshold = 1
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source)
            said = ""

        try:
            said = r.recognize_google(audio)
            print(said)
        except sr.UnknownValueError:
            speak("Didn't get that")
        except sr.RequestError as e:
            speak(f"Speech recognition error: {e}")
        return said.lower()

    def speak_text(self):
        self.label.setText("Speak now...")
        QTimer.singleShot(1000, self.start_microphone)

    def start_microphone(self):
        recog1 = sr.Recognizer()
        mc = sr.Microphone()

        with mc as source:
            recog1.adjust_for_ambient_noise(source, duration=0.2)
            try:
                audio = recog1.listen(source, timeout=5, phrase_time_limit=10)
                MyText = recog1.recognize_google(audio)
                MyText = MyText.lower()
                self.text_input.setText(MyText)
                self.search_movie()
            except sr.WaitTimeoutError:
                self.label.setText(
                    "Listening timed out while waiting for phrase to start"
                )
            except sr.UnknownValueError:
                self.label.setText("Unable to Understand the Input")
            except sr.RequestError as e:
                self.label.setText(f"Unable to provide Required Output: {e}")

    def search_movie(self):
        moviesdb = imdb.IMDb()
        text = self.text_input.text()
        if not text:
            text = self.get_audio()
            self.text_input.setText(text)

        try:
            movies = moviesdb.search_movie(text)
        except imdb.IMDbError as e:
            speak(f"Error accessing IMDb: {e}")
            self.movie_details.setPlainText(f"Error accessing IMDb: {e}")
            return

        speak("Searching for " + text)
        self.movie_details.clear()

        if len(movies) == 0:
            speak("No result found")
            self.movie_details.setPlainText("No result found")
        else:
            speak("I found these:")
            for movie in movies:
                title = movie["title"]
                year = movie["year"]
                info = movie.getID()
                try:
                    movie = moviesdb.get_movie(info)
                except imdb.IMDbError as e:
                    speak(f"Error retrieving movie details: {e}")
                    self.movie_details.setPlainText(
                        f"Error retrieving movie details: {e}"
                    )
                    return

                title = movie["title"]
                year = movie["year"]
                rating = movie.get("rating", "N/A")
                plot = movie.get("plot outline", "No plot available")

                if year < int(datetime.datetime.now().strftime("%Y")):
                    details = f"{title} was released in {year} and has an IMDB rating of {rating}. The plot summary of the movie is: {plot}"
                else:
                    details = f"{title} will release in {year} and has an IMDB rating of {rating}. The plot summary of the movie is: {plot}"

                self.movie_details.append(details)
                break

    def speak_movie_details(self):
        details = self.movie_details.toPlainText()
        speak(details)

    def load_stylesheet(self, path):
        style_sheet = ""
        with open(path, "r") as file:
            style_sheet = file.read()
        self.setStyleSheet(style_sheet)

    def load_stylesheets(self):
        if self.is_dark_mode():
            self.load_stylesheet("DarkUI.css")
        else:
            self.load_stylesheet("STYLESHEETS/Movie_LightUI.css")

    def is_dark_mode(self):
        # Detect dark mode (placeholder for actual dark mode detection logic)
        return False

    def check_and_update_theme(self):
        if self.is_dark_mode():
            self.load_stylesheet("DarkUI.css")
        else:
            self.load_stylesheet("./STYLESHEETS/Movie_LightUI.css")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MovieSearchApp()
    window.show()
    sys.exit(app.exec())
