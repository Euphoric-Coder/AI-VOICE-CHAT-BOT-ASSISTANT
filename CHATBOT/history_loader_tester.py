import os

history_file = "conversation_history.txt"


def load_full_history(history_file):
    """Load and return the full conversation history as user-AI pairs from the text file."""
    history = []
    if os.path.exists(history_file):
        with open(history_file, "r") as file:
            conversation = file.read().strip().split("User: ")
            for entry in conversation[1:]:  # Skip the first split element if it's empty
                parts = entry.split("InsightAI (HTML): ")
                if len(parts) == 2:
                    user_message = parts[0].strip()
                    ai_message = parts[1].strip()  # Captures entire AI response
                    history.append((user_message, ai_message))
    return history


print(load_full_history(history_file="conversation_history.txt"))
