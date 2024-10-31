import os
import csv
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QScrollArea,
    QFrame,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint
from PyQt6.QtGui import QTextCursor, QPalette, QColor
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


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
        ai_response = res.content  # Assume content is HTML

        # Generate a 20-word summary of the response
        summary = self._generate_summary(ai_response)

        # Determine if the AI provided a response (prompt_given)
        prompt_given = "yes" if ai_response else "no"

        # Log the question, prompt status, and summary in CSV
        self._log_to_csv(question, prompt_given, summary)

        # Append full conversation in HTML to the text history file
        self._append_to_history_file(question, ai_response)

        # Update the conversation context with a summary of the latest question and prompt status
        self.context += f"\nUser Question: {question} | Prompt Given: {prompt_given} | Summary: {summary}"

        return ai_response


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.bot = InsightBot()
        self.setWindowTitle("InsightBot Chat")
        self.setGeometry(100, 100, 500, 600)
        self.setStyleSheet("background-color: #2c3e50; color: #ecf0f1;")

        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Chat display area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        # Input area with a floating style
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.returnPressed.connect(self.handle_user_input)
        self.layout.addWidget(self.input_field)

        # Set styles for a professional look
        self.scroll_area.setStyleSheet("border: none; background-color: #34495e;")
        self.scroll_layout.setSpacing(10)
        self.input_field.setStyleSheet(
            """
            QLineEdit {
                background-color: #1abc9c;
                color: #2c3e50;
                padding: 10px;
                border-radius: 15px;
                border: none;
                margin: 10px;
            }
            QLineEdit:hover {
                background-color: #16a085;
            }
        """
        )

    def add_message(self, message, sender="User"):
        message_label = QLabel()
        message_label.setWordWrap(True)
        message_label.setTextFormat(Qt.TextFormat.RichText)  # Enable HTML formatting
        message_label.setText(message)

        # Style messages differently for user and bot
        if sender == "User":
            message_label.setStyleSheet(
                "background-color: #3498db; color: #ecf0f1; padding: 10px; border-radius: 15px;"
            )
            align_layout = QHBoxLayout()
            align_layout.addStretch()
            align_layout.addWidget(message_label)
        else:
            message_label.setStyleSheet(
                "background-color: #e67e22; color: #ecf0f1; padding: 10px; border-radius: 15px;"
            )
            align_layout = QHBoxLayout()
            align_layout.addWidget(message_label)
            align_layout.addStretch()

        # Add message to scroll layout
        container = QWidget()
        container.setLayout(align_layout)
        self.scroll_layout.addWidget(container)

        # Smooth scroll to the latest message
        QTimer.singleShot(50, lambda: self.scroll_to_bottom())

    def handle_user_input(self):
        user_input = self.input_field.text()
        if not user_input.strip():
            return
        self.add_message(user_input, sender="User")
        self.input_field.clear()

        # Get AI response in HTML format
        ai_response = self.bot.Chat(user_input)
        self.add_message(ai_response, sender="InsightAI")

    def scroll_to_bottom(self):
        """Smoothly scroll to the bottom of the chat display area."""
        scroll_bar = self.scroll_area.verticalScrollBar()
        animation = QPropertyAnimation(scroll_bar, b"value")
        animation.setDuration(500)
        animation.setStartValue(scroll_bar.value())
        animation.setEndValue(scroll_bar.maximum())
        animation.start()


if __name__ == "__main__":
    import sys
    from PyQt6.QtCore import QTimer

    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())
