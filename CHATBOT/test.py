import os
import csv
import subprocess
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def macos_theme():
    """Checks DARK/LIGHT mode of macOS."""
    cmd = "defaults read -g AppleInterfaceStyle"
    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    return bool(p.communicate()[0])


class InsightBot:
    def __init__(
        self,
        history_file="conversation_history.txt",
        csv_file="conversation_summary.csv",
    ):
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-70b-versatile",
        )
        self.history_file = history_file
        self.csv_file = csv_file
        self.context = self._load_history_summary()

    def _load_history_summary(self):
        summary = ""
        if os.path.exists(self.csv_file):
            with open(self.csv_file, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    summary += f"User Question: {row['question']} | Prompt Given: {row['prompt_given']} | Summary: {row['summary']}\n"
        return summary

    def _log_to_csv(self, question, prompt_given, summary):
        file_exists = os.path.exists(self.csv_file)
        with open(self.csv_file, "a", newline="") as file:
            writer = csv.DictWriter(
                file, fieldnames=["question", "prompt_given", "summary"]
            )
            if not file_exists:
                writer.writeheader()
            writer.writerow(
                {"question": question, "prompt_given": prompt_given, "summary": summary}
            )

    def _append_to_history_file(self, user_input, ai_response):
        with open(self.history_file, "a") as file:
            file.write(f"User: {user_input}\nInsightAI (HTML): {ai_response}\n\n")

    def load_full_history(self):
        history = []
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as file:
                conversation = file.read().strip().split("User: ")
                for entry in conversation[1:]:
                    parts = entry.split("InsightAI (HTML): ")
                    if len(parts) == 2:
                        user_message = parts[0].strip()
                        ai_message = parts[1].strip()
                        history.append((user_message, ai_message))
        return history

    def _generate_summary(self, text):
        prompt = PromptTemplate.from_template(
            """
            Summarize the following content in 20 words or fewer:
            
            Content: {text}
            
            Summary:
            """
        )
        summary_chain = prompt | self.llm
        result = summary_chain.invoke({"text": text})
        return result.content.strip()

    def Chat(self, question):
        prompt = PromptTemplate.from_template(
            """
            Answer the question(s) below asked by the User.

            Here is the conversation history summary:
            {context}

            Question: {question}

            Answer in HTML format:
            """
        )
        chain_extract = prompt | self.llm
        res = chain_extract.invoke({"context": self.context, "question": question})
        ai_response = res.content
        summary = self._generate_summary(ai_response)
        prompt_given = "yes" if ai_response else "no"
        self._log_to_csv(question, prompt_given, summary)
        self._append_to_history_file(question, ai_response)
        self.context += f"\nUser Question: {question} | Prompt Given: {prompt_given} | Summary: {summary}"
        return ai_response


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.bot = InsightBot()
        self.setWindowTitle("InsightBot Chat")

        # Set minimum and maximum size for the chat window
        self.setMinimumWidth(700)
        self.setMaximumSize(1200, 800)

        # Disable the maximize button
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowCloseButtonHint
        )

        # Set object names for components
        self.setObjectName("mainWindow")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Chat display area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scrollArea")

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scrollContent")

        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        # Input and theme toggle layout
        input_layout = QHBoxLayout()
        input_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Theme toggle button as an icon
        self.theme_toggle_button = QPushButton()
        self.theme_toggle_button.setObjectName("themeToggleButton")
        self.theme_toggle_button.setFixedSize(30, 30)
        self.theme_toggle_button.setIconSize(
            QSize(20, 20)
        )  # Fixed icon size to prevent shifting
        self.theme_toggle_button.clicked.connect(self.toggle_theme)

        # Initial theme and button styling
        self.current_theme = None
        self.load_initial_theme()

        input_layout.addWidget(self.theme_toggle_button)

        # Input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask something...")
        self.input_field.setObjectName("inputField")
        input_layout.addWidget(self.input_field)
        self.input_field.returnPressed.connect(self.handle_user_input)

        # Add input layout to the main layout
        self.layout.addLayout(input_layout)

        # Load chat history on startup
        self.load_chat_history()

    def load_stylesheet(self, path):
        """Load a stylesheet from a file."""
        with open(path, "r") as file:
            style_sheet = file.read()
            self.setStyleSheet(style_sheet)

    def load_initial_theme(self):
        """Load light or dark theme based on initial macOS theme and set the icon and background color."""
        if macos_theme():
            self.load_stylesheet("./STYLESHEETS/ChatDarkUI.css")
            self.current_theme = "dark"
            self.theme_toggle_button.setIcon(
                QIcon("sun_icon.png")
            )  # Set to sun icon for dark mode
            self.theme_toggle_button.setStyleSheet(
                """
                QPushButton {
                    border: none;
                    background-color: #f0c674;  /* Light yellow background for dark mode */
                    border-radius: 15px;
                }
                QPushButton:hover {
                    background-color: #f5d799;  /* Lighter yellow on hover */
                }
            """
            )
        else:
            self.load_stylesheet("./STYLESHEETS/ChatLightUI.css")
            self.current_theme = "light"
            self.theme_toggle_button.setIcon(
                QIcon("moon_icon.png")
            )  # Set to moon icon for light mode
            self.theme_toggle_button.setStyleSheet(
                """
                QPushButton {
                    border: none;
                    background-color: #333333;  /* Dark gray background for light mode */
                    border-radius: 15px;
                }
                QPushButton:hover {
                    background-color: #555555;  /* Lighter gray on hover */
                }
            """
            )

    def toggle_theme(self):
        """Manually toggle between light and dark themes, updating the icon and button background color."""
        if self.current_theme == "dark":
            self.load_stylesheet("./STYLESHEETS/ChatLightUI.css")
            self.current_theme = "light"
            self.theme_toggle_button.setIcon(
                QIcon("moon_icon.png")
            )  # Switch to moon icon for light mode
            self.theme_toggle_button.setStyleSheet(
                """
                QPushButton {
                    border: none;
                    background-color: #333333;  /* Dark gray background */
                    border-radius: 15px;
                }
                QPushButton:hover {
                    background-color: #555555;  /* Lighter gray on hover */
                }
            """
            )
        else:
            self.load_stylesheet("./STYLESHEETS/ChatDarkUI.css")
            self.current_theme = "dark"
            self.theme_toggle_button.setIcon(
                QIcon("sun_icon.png")
            )  # Switch to sun icon for dark mode
            self.theme_toggle_button.setStyleSheet(
                """
                QPushButton {
                    border: none;
                    background-color: #f0c674;  /* Light yellow background */
                    border-radius: 15px;
                }
                QPushButton:hover {
                    background-color: #f5d799;  /* Lighter yellow on hover */
                }
            """
            )

    def load_chat_history(self):
        history = self.bot.load_full_history()
        for user_message, ai_response in history:
            self.add_message(user_message, sender="User")
            self.add_message(ai_response, sender="Bot")

    def add_message(self, message, sender="User"):
        align_layout = QHBoxLayout()

        if sender == "User":
            message_label = QLabel(message)
            message_label.setWordWrap(True)
            message_label.setTextFormat(Qt.TextFormat.PlainText)
            message_label.setFixedWidth(int(self.width() * 0.4))
            message_label.setObjectName("messageUser")
            align_layout.addStretch()
            align_layout.addWidget(message_label)

        else:
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(10, 5, 10, 5)
            container.setObjectName("messageContainer")

            message_label = QLabel()
            message_label.setWordWrap(True)
            message_label.setTextFormat(Qt.TextFormat.RichText)
            message_label.setText(message)
            message_label.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
            )
            message_label.setObjectName("messageBot")

            container_layout.addWidget(message_label)
            align_layout.addWidget(container)
            align_layout.addStretch()

        wrapper = QWidget()
        wrapper.setLayout(align_layout)
        self.scroll_layout.addWidget(wrapper)

        QTimer.singleShot(50, lambda: self.scroll_to_bottom())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        for i in range(self.scroll_layout.count()):
            container = self.scroll_layout.itemAt(i).widget()
            if container:
                layout = container.layout()
                label = layout.itemAt(1 if layout.count() > 1 else 0).widget()
                if label and isinstance(label, QLabel):
                    if label.objectName() == "messageUser":
                        label.setFixedWidth(int(self.width() * 0.4))
                    else:
                        label.setSizePolicy(
                            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
                        )

    def handle_user_input(self):
        user_input = self.input_field.text()
        if user_input.strip():
            self.add_message(user_input, sender="User")
            self.input_field.clear()
            ai_response = self.bot.Chat(user_input)
            self.add_message(ai_response, sender="Bot")

    def scroll_to_bottom(self):
        scroll_bar = self.scroll_area.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())
