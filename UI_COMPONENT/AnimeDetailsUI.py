from AnilistPython import Anilist

anime = Anilist()

try:
    print(anime.print_anime_info(input("Please enter the name of Anime:\n")))
except Exception as e:
    print(f"Sorry!!! The Anime that you are searching for is not present or does not exist!!!!")


import sys
import os

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


class AnimeUI(QDialog):
    def __init__(self):
        super().__init__()

        # Set the dialog title
        self.setWindowTitle("Anime")
        self.setMinimumSize(800, 600)

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
    dialog = AnimeUI()
    dialog.exec()

    # Clean exit
    sys.exit(app.exec())


if __name__ == "__main__":
    main()