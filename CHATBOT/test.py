import os
import csv
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
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
        """Append the entire user-AI conversation pair to the text file."""
        with open(self.history_file, "a") as file:
            file.write(f"User: {user_input}\nInsightAI (HTML): {ai_response}\n\n")

    def load_full_history(self):
        """Load and return the full conversation history as user-AI pairs from the text file."""
        history = []
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as file:
                conversation = file.read().strip().split("User: ")
                for entry in conversation[
                    1:
                ]:  # Skip the first split element if it's empty
                    parts = entry.split("InsightAI (HTML): ")
                    if len(parts) == 2:
                        user_message = parts[0].strip()
                        ai_message = parts[1].strip()  # Captures entire AI response
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
        self.setGeometry(100, 100, 800, 700)
        self.setStyleSheet("background-color: #1c2833; color: #f7f9f9;")

        # Main layout
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
        self.input_field.setPlaceholderText("Ask something...")
        self.input_field.returnPressed.connect(self.handle_user_input)
        self.layout.addWidget(self.input_field)

        # Set styles for a modern UI
        self.scroll_area.setStyleSheet("border: none; background-color: #273746;")
        self.scroll_layout.setSpacing(12)
        self.input_field.setStyleSheet(
            """
            QLineEdit {
                background-color: #34495e;
                color: #ecf0f1;
                padding: 10px;
                border-radius: 20px;
                margin: 15px;
                border: 1px solid #1abc9c;
            }
            QLineEdit:hover {
                background-color: #1abc9c;
                color: #34495e;
            }
        """
        )

        # Load chat history on startup
        self.load_chat_history()

    def load_chat_history(self):
        """Load and display chat history from the conversation_history.txt file."""
        history = self.bot.load_full_history()
        for user_message, ai_response in history:
            self.add_message(user_message, sender="User")
            self.add_message(ai_response, sender="InsightAI")

    def add_message(self, message, sender="User"):
        message_label = QLabel()
        message_label.setWordWrap(True)
        message_label.setTextFormat(Qt.TextFormat.RichText)  # Enable HTML formatting
        message_label.setText(message)

        align_layout = QHBoxLayout()

        if sender == "User":
            # User message limited to 40% of window width, aligned to the right
            message_label.setFixedWidth(int(self.width() * 0.4))
            message_label.setStyleSheet(
                """
                background-color: #3498db; color: #ecf0f1; padding: 10px; 
                border-radius: 15px; margin: 5px 10px 5px 80px;
                """
            )
            align_layout.addStretch()  # Adds stretch on the left
            align_layout.addWidget(message_label)  # Adds user message aligned to the right
        else:
            # Bot message set to expand fully, aligned to the left
            message_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            message_label.setStyleSheet(
                """
                background-color: #e67e22; color: #ecf0f1; padding: 10px; 
                border-radius: 15px; margin: 5px 80px 5px 10px;
                """
            )
            align_layout.addWidget(message_label)  # Adds bot message aligned to the left
            align_layout.addStretch()  # Adds stretch on the right to keep alignment

        # Add the message to the scroll layout
        container = QWidget()
        container.setLayout(align_layout)
        self.scroll_layout.addWidget(container)

        # Refresh layout dynamically on window resize
        self.scroll_content.adjustSize()
        self.scroll_layout.update()
        
        # Smooth scroll to the latest message
        QTimer.singleShot(50, lambda: self.scroll_to_bottom())

    def handle_user_input(self):
        user_input = self.input_field.text()
        if not user_input.strip():
            return
        self.add_message(user_input, sender="User")
        self.input_field.clear()

        # Get AI response in HTML format and display
        ai_response = self.bot.Chat(user_input)
        self.add_message(ai_response, sender="InsightAI")

    def scroll_to_bottom(self):
        """Smoothly scroll to the bottom of the chat display area."""
        scroll_bar = self.scroll_area.verticalScrollBar()
        animation = QPropertyAnimation(scroll_bar, b"value")
        animation.setDuration(700)
        animation.setStartValue(scroll_bar.value())
        animation.setEndValue(scroll_bar.maximum())
        animation.start()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())