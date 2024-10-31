from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
import sys


class LinkPreviewer(QDialog):
    def __init__(self, *args, **kwargs):
        super(LinkPreviewer, self).__init__(*args, **kwargs)

        layout = QVBoxLayout()
        self.setLayout(layout)

        navtb = QToolBar("Navigation")
        self.setGeometry(200, 300, 800, 600)
        navtb.setIconSize(QSize(16, 16))

        self.urlbar = QLineEdit()
        self.urlbar.setText("https://www.youtube.com")
        self.urlbar.setReadOnly(True)
        navtb.addWidget(self.urlbar)
        layout.addWidget(navtb)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(self.urlbar.text()))
        layout.addWidget(self.browser)

        self.show()

    def keyPressEvent(self, event):
        # Handle Ctrl+W (Windows/Linux) or Cmd+W (MacOS) to close the window
        if event.key() == Qt.Key.Key_W and (
            event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load external QSS file
    try:
        with open("style.css") as f:
            style_sheet = f.read()
        app.setStyleSheet(style_sheet)
    except FileNotFoundError:
        print("style.css not found, continuing without stylesheet")

    window = LinkPreviewer()
    sys.exit(app.exec())
