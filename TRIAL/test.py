import sys
from PyQt6.QtWidgets import QApplication, QLineEdit, QVBoxLayout, QWidget
from PyQt6.QtGui import QPainter, QTextLayout, QPalette, QColor, QTextOption
from PyQt6.QtCore import Qt, QPointF


class CustomLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selection_bg_color = QColor("#87CEFA")  # Light Sky Blue
        self.selection_text_color = QColor("#FFFFFF")  # White

    def paintEvent(self, event):
        painter = QPainter(self)
        option = self.style().standardPalette()

        # Draw the background
        if self.isEnabled():
            bg_color = self.palette().color(QPalette.ColorRole.Base)
        else:
            bg_color = self.palette().color(QPalette.ColorRole.Window)

        painter.fillRect(self.rect(), bg_color)

        # Draw the text
        text = self.text()
        if not text:
            return

        layout = QTextLayout(text, self.font())
        layout.setTextOption(self.textOption())

        pen = QPalette().color(QPalette.ColorRole.Text)
        if self.isEnabled():
            pen = self.palette().color(QPalette.ColorRole.Text)
        else:
            pen = self.palette().color(QPalette.ColorRole.WindowText)

        cursor_pos = self.cursorPosition()
        selection_start = self.selectionStart()
        selection_length = len(self.selectedText())

        layout.beginLayout()
        line = layout.createLine()
        line.setLineWidth(self.width())
        line.setPosition(QPointF(self.rect().topLeft()))  # Convert to QPointF
        layout.endLayout()

        layout.draw(painter, QPointF(self.rect().topLeft()))  # Convert to QPointF

        # Draw the selection background
        if selection_length > 0:
            selection_rect = self.cursorRect()
            selection_rect.setLeft(selection_rect.left() + selection_start)
            selection_rect.setWidth(selection_length)
            painter.fillRect(selection_rect, self.selection_bg_color)

            # Draw the selected text
            painter.setPen(self.selection_text_color)
            layout.draw(painter, QPointF(self.rect().topLeft()))  # Convert to QPointF

        painter.end()

    def textOption(self):
        option = QTextOption()
        option.setWrapMode(QTextOption.WrapMode.NoWrap)
        return option


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.line_edit = CustomLineEdit(self)
        layout.addWidget(self.line_edit)

        self.setLayout(layout)
        self.setWindowTitle("Custom QLineEdit Selection Example")
        self.setGeometry(100, 100, 400, 200)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
