from gnewsclient import gnewsclient

client = gnewsclient.NewsClient(
    language="english", location="india", topic="sports", max_results=100
)

news_list = client.get_news()

for item in news_list:
    print("Title : ", item["title"])
    print("Link : ", item["link"])
    print("")


import sys
import os

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


class NewsFeedUI(QDialog):
    def __init__(self):
        super().__init__()

        # Set the dialog title
        self.setWindowTitle("News Feed")
        self.setMinimumSize(800, 500)

        # Set the layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add a label
        label = QLabel("This is a PyQt6 QDialog")
        layout.addWidget(label)

        # Add a button
        button = QPushButton("Close")
        button.clicked.connect(self.accept)  # Close the dialog on button click
        layout.addWidget(button)

        # Set the dialog size
        self.resize(300, 200)


def main():
    # Create the application
    app = QApplication(sys.argv)

    # Create and show the dialog
    dialog = NewsFeedUI()
    dialog.exec()

    # Clean exit
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

