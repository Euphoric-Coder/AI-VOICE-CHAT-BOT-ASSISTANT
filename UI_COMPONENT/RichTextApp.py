import os
import re
import sys
import subprocess
from posixpath import splitext
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtPrintSupport import *

sizes_of_font = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]
HTML_EXTENSIONS = ['.html', '.htm']
global style
style = "Comic Sans MS"

# Declared the global variable to avoid error when initializing
window = None


# GOT A HOLD OF THIS CODE FROM STALK OVERFLOW. HERE IS THE CODE
# https://stackoverflow.com/questions/65294987/detect-os-dark-mode-in-python
def macos_theme():
    """Checks DARK/LIGHT mode of macos."""
    cmd = "defaults read -g AppleInterfaceStyle"
    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    return bool(p.communicate()[0])


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Mail Composer")
    ex = MingleComposer()
    ex.show()
    sys.exit(app.exec())


def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def check(emails):
    f = False
    # pass the regular expression
    matcher = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    # and the string into the fullmatch() method
    for email in emails.split(", "):
        if re.fullmatch(matcher, email):
            f = True
        else:
            f = False
    return f


class LinkInsertionDialog(QDialog):
    link_inserted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Insert Link")
        self.link_text_edit = QLineEdit(self)
        self.link_url_edit = QLineEdit(self)
        insert_button = QPushButton("Insert", self)
        insert_button.clicked.connect(self.insert_link)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Link Text:"))
        layout.addWidget(self.link_text_edit)
        layout.addWidget(QLabel("Link URL:"))
        layout.addWidget(self.link_url_edit)
        layout.addWidget(insert_button)

    def insert_link(self):
        link_text = self.link_text_edit.text()
        link_url = self.link_url_edit.text()

        if link_text and link_url:
            link_html = f'<a href="{link_url}">{link_text}</a> <br />'
            self.link_inserted.emit(link_html)
            self.close()
        else:
            # Handle the case where either link text or link URL is empty
            self.reject()
            # print("Both link text and link URL are required.")


class ModifyAttachmentWindow(QDialog):
    def __init__(self, attachment_paths):
        super().__init__()
        self.attachment_paths = attachment_paths.copy()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.checkboxes = []

        # Create checkboxes for each attachment path
        for path in self.attachment_paths:
            checkbox = QCheckBox(path)
            checkbox.setChecked(False)
            layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)

        # Create a button to apply changes
        apply_button = QPushButton("Remove")
        apply_button.clicked.connect(self.applyChanges)
        layout.addWidget(apply_button)

        self.setLayout(layout)
        self.setWindowTitle("Modify Attachments")
        self.show()

    def applyChanges(self):
        # Remove checked files from the attachment_paths list
        self.attachment_paths = [
            path
            for path in self.attachment_paths
            if path
            not in [
                checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()
            ]
        ]
        self.close()


class CustomTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursorPositionChanged.connect(self.update_formatting_actions)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            cursor = self.textCursor()
            current_block_format = cursor.blockFormat()
            new_block = QTextBlockFormat()

            # Copy the alignment from the current block to the new block
            new_block.setAlignment(current_block_format.alignment())

            cursor.setBlockFormat(new_block)
            cursor.insertBlock()
            self.ensureCursorVisible()
        else:
            super().keyPressEvent(event)

    def update_formatting_actions(self):
        cursor = self.textCursor()
        char_format = cursor.charFormat()
        block_format = cursor.blockFormat()
        if window != None:
            # Access formatting actions and combo boxes directly
            window.fonts.setCurrentFont(QFont(char_format.font().family()))
            window.fontsize.setCurrentText(str(int(char_format.font().pointSize())))

            window.bold_action.setChecked(char_format.font().bold())
            window.italic_action.setChecked(char_format.font().italic())
            window.underline_action.setChecked(char_format.font().underline())

            window.uncheck_align_actions()
            if block_format.alignment() == Qt.AlignmentFlag.AlignLeft:
                window.align_left_action.setChecked(True)
            elif block_format.alignment() == Qt.AlignmentFlag.AlignCenter:
                window.align_center_action.setChecked(True)
            elif block_format.alignment() == Qt.AlignmentFlag.AlignRight:
                window.align_right_action.setChecked(True)
            elif block_format.alignment() == Qt.AlignmentFlag.AlignJustify:
                window.align_justify_action.setChecked(True)


class MingleComposer(QDialog):
    def __init__(self, mail_content="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_stylesheets()
        self.theme_check_timer = QTimer(self)
        self.theme_check_timer.timeout.connect(self.check_and_update_theme)
        self.theme_check_timer.start(600)

        # Set the minimum size
        self.setMinimumSize(1320, 700)

        # Get screen geometry
        screen = QGuiApplication.primaryScreen().geometry()

        # Get the current size of the window
        window_width = self.frameGeometry().width()
        window_height = self.frameGeometry().height()

        # Center the window on the screen
        self.setGeometry(
            (screen.width() - window_width) // 2,
            (screen.height() - window_height) // 2,
            window_width,
            window_height,
        )

        self.path = None

        layout = QVBoxLayout()
        self.rich_text_editor = CustomTextEdit()
        self.cursor_position = None
        self.rich_text_editor.setHtml(mail_content)

        format_toolbar = QToolBar("Format")
        format_toolbar.setIconSize(QSize(32, 32))
        format_toolbar.setMovable(False)  # Sets the toolbar as non-movable
        layout.addWidget(format_toolbar)

        print_icon = QIcon("UI-IMAGES/print.png")
        self.print_action = QAction(print_icon, "Print", self)
        self.print_action.setStatusTip("Prints the Page")
        self.print_action.setShortcut(QKeySequence.fromString("Ctrl+P"))
        self.print_action.triggered.connect(self.file_print)

        open_icon = QIcon("UI-IMAGES/open.png")
        self.open_action = QAction(open_icon, "Open", self)
        self.open_action.setStatusTip("Opens a File (.html or .txt)")
        self.open_action.setShortcut(QKeySequence.fromString("Ctrl+O"))
        self.open_action.triggered.connect(self.file_open)

        save_icon = QIcon("UI-IMAGES/save.png")
        self.save_action = QAction(save_icon, "Save", self)
        self.save_action.setStatusTip("Saves Current File")
        self.save_action.setShortcut(QKeySequence.fromString("Ctrl+S"))
        self.save_action.triggered.connect(self.file_save)

        saveas_icon = QIcon("UI-IMAGES/saveas.png")
        self.saveas_action = QAction(saveas_icon, "Print", self)
        self.saveas_action.setStatusTip("Saves Current File to Specified file")
        self.saveas_action.setShortcut(QKeySequence.fromString("Ctrl+Shift+S"))
        self.saveas_action.triggered.connect(self.file_saveas)

        format_toolbar.addActions(
            [self.open_action, self.save_action, self.saveas_action, self.print_action]
        )
        format_toolbar.addSeparator()

        self.fonts = QFontComboBox()
        self.fonts.currentFontChanged.connect(self.font_changed)
        format_toolbar.addWidget(self.fonts)

        self.fontsize = QComboBox()
        self.fontsize.addItems([str(s) for s in sizes_of_font])
        self.fontsize.currentIndexChanged.connect(self.font_size_changed)

        format_toolbar.addWidget(self.fontsize)
        format_toolbar.addSeparator()

        # Added Bold, Italics, and Underline on the Toolbar
        bold_icon = QIcon("UI-IMAGES/bold.png")
        self.bold_action = QAction(bold_icon, "Bold", self, checkable=True)
        self.bold_action.setShortcut(QKeySequence.fromString("Ctrl+B"))
        self.bold_action.toggled.connect(self.set_bold)

        italic_icon = QIcon("UI-IMAGES/italic.png")
        self.italic_action = QAction(italic_icon, "Italic", self, checkable=True)
        self.italic_action.setShortcut(QKeySequence.fromString("Ctrl+I"))
        self.italic_action.toggled.connect(self.set_italic)

        underline_icon = QIcon("UI-IMAGES/underline.png")
        self.underline_action = QAction(underline_icon, "Underline", self, checkable=True)
        self.underline_action.setShortcut(QKeySequence.fromString("Ctrl+U"))
        self.underline_action.toggled.connect(self.set_underline)

        format_toolbar.addActions(
            [self.bold_action, self.italic_action, self.underline_action]
        )
        format_toolbar.addSeparator()

        self.align_group = QActionGroup(self)

        self.align_left_action = QAction("Align Left", self, checkable=True)
        self.align_left_action.setIcon(QIcon("UI-IMAGES/align-left.png"))
        self.align_left_action.triggered.connect(self.set_alignment_left)
        self.align_group.addAction(self.align_left_action)
        self.align_left_action.setShortcut(QKeySequence.fromString("Ctrl+L"))

        self.align_center_action = QAction("Align Center", self, checkable=True)
        self.align_center_action.setIcon(QIcon("UI-IMAGES/align-center.png"))
        self.align_center_action.triggered.connect(self.set_alignment_center)
        self.align_group.addAction(self.align_center_action)
        self.align_center_action.setShortcut(QKeySequence.fromString("Ctrl+E"))

        self.align_right_action = QAction("Align Right", self, checkable=True)
        self.align_right_action.setIcon(QIcon("UI-IMAGES/align-right.png"))
        self.align_right_action.triggered.connect(self.set_alignment_right)
        self.align_group.addAction(self.align_right_action)
        self.align_right_action.setShortcut(QKeySequence.fromString("Ctrl+R"))

        self.align_justify_action = QAction("Align Justify", self, checkable=True)
        self.align_justify_action.setIcon(QIcon("UI-IMAGES/align-justify.png"))
        self.align_justify_action.triggered.connect(self.set_alignment_justify)
        self.align_group.addAction(self.align_justify_action)
        self.align_justify_action.setShortcut(QKeySequence.fromString("Ctrl+J"))

        format_toolbar.addActions(
            [
                self.align_left_action,
                self.align_center_action,
                self.align_right_action,
                self.align_justify_action,
            ]
        )
        format_toolbar.addSeparator()

        # Add the new actions for text highlighting, text color, and link to the Toolbar
        self.link_action = QAction("Insert Link", self)
        self.link_action.setIcon(QIcon("UI-IMAGES/link.png"))  # Set your link icon
        self.link_action.triggered.connect(self.show_link_insertion_dialog)

        highlight_icon = QIcon("UI-IMAGES/highlight.png")
        self.highlight_action = QAction(highlight_icon, "Highlight", self)
        self.highlight_action.triggered.connect(self.set_highlight)

        text_color_icon = QIcon("UI-IMAGES/text-color.png")
        self.text_color_action = QAction(text_color_icon, "Text Color", self)
        self.text_color_action.triggered.connect(self.set_text_color)
        
        format_toolbar.addActions([self.link_action, self.highlight_action, self.text_color_action])

        self.fonts.setCurrentFont(QFont("Comic Sans MS"))
        self.fontsize.setCurrentIndex(7)

        self.rich_text_editor.cursorPositionChanged.connect(self.update_formatting_actions)

        # Sets the default Font & Font Style
        self.font = QFont(style, 14)
        self.rich_text_editor.setFont(self.font)
        self.rich_text_editor.setFontPointSize(14)

        layout.addWidget(self.rich_text_editor)
        container = QWidget()
        container.setLayout(layout)
        self.setLayout(layout)

        self.mode_updater()
        self.update_title()
        self.AppFocusSetter()
        self.show()

    def mode_stopper(self, objects, b):
        for o in objects:
            o.blockSignals(b)

    def mode_updater(self):
        self.mode_stopper(
            [self.bold_action, self.italic_action, self.underline_action], True
        )

        cursor = self.rich_text_editor.textCursor()
        char_format = cursor.charFormat()

        self.bold_action.setChecked(char_format.font().bold())
        self.italic_action.setChecked(char_format.font().italic())
        self.underline_action.setChecked(char_format.font().underline())

        self.mode_stopper(
            [self.bold_action, self.italic_action, self.underline_action], False
        )

        self.mode_stopper(
            [
                self.align_left_action,
                self.align_center_action,
                self.align_right_action,
                self.align_justify_action,
            ],
            True,
        )
        alignment = cursor.blockFormat().alignment()

        self.align_left_action.setChecked(alignment == Qt.AlignmentFlag.AlignLeft)
        self.align_center_action.setChecked(alignment == Qt.AlignmentFlag.AlignCenter)
        self.align_right_action.setChecked(alignment == Qt.AlignmentFlag.AlignRight)
        self.align_justify_action.setChecked(alignment == Qt.AlignmentFlag.AlignJustify)

        self.mode_stopper(
            [
                self.align_left_action,
                self.align_center_action,
                self.align_right_action,
                self.align_justify_action,
            ],
            False,
        )

    def font_size_changed(self, index):
        size = float(self.fontsize.itemText(index))
        cursor = self.rich_text_editor.textCursor()

        # Preserve existing formatting and only change font size
        char_format = QTextCharFormat()
        char_format.setFontPointSize(size)

        # Apply the modified character format to the selected text
        cursor.mergeCharFormat(char_format)
        self.rich_text_editor.setTextCursor(cursor)

        self.rich_text_editor.setFocus()
        self.mode_updater()

    def update_formatting_actions(self):
        cursor = self.rich_text_editor.textCursor()
        char_format = cursor.charFormat()
        block_format = cursor.blockFormat()

        # Update font style and size actions
        self.fonts.setCurrentFont(QFont(char_format.font().family()))
        self.fontsize.setCurrentText(str(int(char_format.font().pointSize())))

        self.bold_action.setChecked(char_format.font().bold())
        self.italic_action.setChecked(char_format.font().italic())
        self.underline_action.setChecked(char_format.font().underline())

        self.uncheck_align_actions()
        if block_format.alignment() == Qt.AlignmentFlag.AlignLeft:
            self.align_left_action.setChecked(True)
        elif block_format.alignment() == Qt.AlignmentFlag.AlignCenter:
            self.align_center_action.setChecked(True)
        elif block_format.alignment() == Qt.AlignmentFlag.AlignRight:
            self.align_right_action.setChecked(True)
        elif block_format.alignment() == Qt.AlignmentFlag.AlignJustify:
            self.align_justify_action.setChecked(True)

    def font_changed(self, font):
        cursor = self.rich_text_editor.textCursor()
        char_format = cursor.charFormat()

        # Preserve existing formatting properties and only change font family
        char_format.setFontFamily(font.family())

        cursor.mergeCharFormat(char_format)
        self.rich_text_editor.setTextCursor(cursor)
        self.rich_text_editor.setFocus()
        self.mode_updater()
        style = self.rich_text_editor.currentFont().family()

    def font_size_changed(self, index):
        size = float(self.fontsize.itemText(index))
        cursor = self.rich_text_editor.textCursor()

        # Preserve existing formatting and only change font size
        char_format = QTextCharFormat()
        char_format.setFontPointSize(size)

        # Apply the modified character format to the selected text
        cursor.mergeCharFormat(char_format)
        self.rich_text_editor.setTextCursor(cursor)

        self.rich_text_editor.setFocus()
        self.mode_updater()

    def set_bold(self, bold):
        font = self.rich_text_editor.currentFont()
        font.setBold(bold)
        self.rich_text_editor.setCurrentFont(font)
        self.rich_text_editor.setFocus()
        self.mode_updater()

    def set_italic(self, italic):
        font = self.rich_text_editor.currentFont()
        font.setItalic(italic)
        self.rich_text_editor.setCurrentFont(font)
        self.rich_text_editor.setFocus()
        self.mode_updater()

    def set_underline(self, underline):
        font = self.rich_text_editor.currentFont()
        font.setUnderline(underline)
        self.rich_text_editor.setCurrentFont(font)
        self.rich_text_editor.setFocus()
        self.mode_updater()

    def uncheck_align_actions(self):
        for action in self.align_group.actions():
            action.setChecked(False)

    def set_alignment_left(self):
        self.uncheck_align_actions()
        self.set_alignment(Qt.AlignmentFlag.AlignLeft)

    def set_alignment_center(self):
        self.uncheck_align_actions()
        self.set_alignment(Qt.AlignmentFlag.AlignCenter)

    def set_alignment_right(self):
        self.uncheck_align_actions()
        self.set_alignment(Qt.AlignmentFlag.AlignRight)

    def set_alignment_justify(self):
        self.uncheck_align_actions()
        self.set_alignment(Qt.AlignmentFlag.AlignJustify)

    def set_alignment(self, alignment):
        cursor = self.rich_text_editor.textCursor()
        block_format = cursor.blockFormat()

        # Check if the provided alignment is the same as the current alignment
        if block_format.alignment() == alignment:
            # Set alignment to default left alignment if it's the same as current alignment
            alignment = Qt.AlignmentFlag.AlignLeft

        block_format.setAlignment(alignment)
        cursor.mergeBlockFormat(block_format)
        self.rich_text_editor.setTextCursor(cursor)
        self.rich_text_editor.setFocus()
        self.mode_updater()
        self.update_title()

    def set_highlight(self):
        color = QColorDialog.getColor()
        if color.isValid():
            cursor = self.rich_text_editor.textCursor()
            format = QTextCharFormat()
            format.setBackground(color)
            cursor.mergeCharFormat(format)

    def set_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            cursor = self.rich_text_editor.textCursor()
            format = QTextCharFormat()
            format.setForeground(color)

            if cursor.hasSelection():
                # If text is selected, change the color of the selected text
                cursor.mergeCharFormat(format)
            else:
                # If no text is selected, change the color of the current word or the current block
                cursor.select(QTextCursor.SelectionType.WordUnderCursor)
                cursor.mergeCharFormat(format)
                cursor.clearSelection()
                cursor.setCharFormat(
                    format
                )  # Apply the format to the current position as well

            self.rich_text_editor.setTextCursor(cursor)

    def AppFocusSetter(self):
        """
        This method sets Focus to the Text Editor, making it ready for user input ASAP
        """
        self.rich_text_editor.setFocus()

    def open_file_dialog(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("All Files (*)")
        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            for file in files:
                if file not in self.attachment_paths:
                    self.attachment_paths.append(file)
            self.update_attachment_list()

    def load_stylesheet(self, path):
        style_sheet = ""
        with open(path, "r") as file:
            style_sheet = file.read()
        self.setStyleSheet(style_sheet)

    def load_stylesheets(self):
        if macos_theme() == False:
            self.load_stylesheet("LightUI.css")
        else:
            self.load_stylesheet("DarkUI.css")

    def check_and_update_theme(self):
        if macos_theme() == False:
            self.load_stylesheet("LightUI.css")
        else:
            self.load_stylesheet("DarkUI.css")

    def show_link_insertion_dialog(self):
        link_dialog = LinkInsertionDialog(self)
        link_dialog.link_inserted.connect(self.insert_link_at_cursor)
        link_dialog.exec()

    def insert_link_at_cursor(self, link_html):
        cursor = self.rich_text_editor.textCursor()
        cursor.insertHtml(link_html)

    def dialog_critical(self, message):
        """
        Display a critical dialog with the given message.
        """
        dlg = QMessageBox(self)
        dlg.setText(message)
        dlg.setIcon(QMessageBox.Icon.Critical)  # Use Icon.Critical for PyQt6
        dlg.show()

    def file_open(self):
        """
        Open a file dialog to select a file, read its contents, and set the rich_text_editor text.
        """
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open file",
            "",
            "HTML documents (*.html);Text documents (*.txt);;"
        )
        if path:  # Check if a file path was selected
            try:
                with open(path, "r") as f:
                    text = f.read()
                self.rich_text_editor.setText(text)  # Set the rich_text_editor's text to the file's content
                self.path = path  # Store the file path
                self.update_title()  # Update the window title to the file name
            except Exception as e:
                self.dialog_critical(str(e))  # Show error message if file read fails

    def file_save(self):
        """
        Save the current document. If no path is set, prompt the user with a Save As dialog.
        """
        if not self.path:  # If no file path is set, use Save As
            return self.file_saveas()

        # Determine the format (HTML or plain text) based on file extension
        text = (
            self.rich_text_editor.toHtml()
            if splitext(self.path)[1] in HTML_EXTENSIONS
            else self.rich_text_editor.toPlainText()
        )
        try:
            with open(self.path, "w") as f:
                f.write(text)  # Write the text to the file
        except Exception as e:
            self.dialog_critical(str(e))  # Show error message if file write fails

    def file_saveas(self):
        """
        Prompt the user with a Save As dialog to save the current document.
        """
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save file",
            "",
            "HTML documents (*.html);Text documents (*.txt);All files (*.*)",
        )
        if path:  # Check if a file path was selected
            # Determine the format (HTML or plain text) based on file extension
            text = (
                self.rich_text_editor.toHtml()
                if splitext(path)[1] in HTML_EXTENSIONS
                else self.rich_text_editor.toPlainText()
            )
            try:
                with open(path, "w") as f:
                    f.write(text)  # Write the text to the file
                self.path = path  # Store the new file path
                self.update_title()  # Update the window title to the new file name
            except Exception as e:
                self.dialog_critical(str(e))  # Show error message if file write fails

    def file_print(self):
        """
        Open the print dialog to print the current document.
        """
        dlg = QPrintDialog()
        if dlg.exec():
            self.rich_text_editor.print_(
                dlg.printer()
            )  # Print the document using the selected printer

    def update_title(self):
        """
        Update the window title based on the current file name.
        """
        self.setWindowTitle(
            f"{os.path.basename(self.path) if self.path else 'Untitled'}"
        )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            event.ignore()  # Ignore the Enter/Return key press
        elif (
            event.key() == Qt.Key.Key_W
        ) and event.modifiers() & (
            Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.MetaModifier
        ):
            # Need to add a feature for save before closing
            print("Closed")
            self.close()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    main()
