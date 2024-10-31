import os
import re
import sys
import subprocess
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

sizes_of_font = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]
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
        self.setMinimumSize(1150, 800)

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

        layout = QVBoxLayout()
        self.mail_composer = CustomTextEdit()
        self.cursor_position = None
        self.mail_composer.setHtml(mail_content)

        # Created a Horizontal Layouts for each button and line edit pair
        to_layout = QHBoxLayout()
        subject_layout = QHBoxLayout()
        cc_layout = QHBoxLayout()
        bcc_layout = QHBoxLayout()

        format_toolbar = QToolBar("Format")
        format_toolbar.setIconSize(QSize(32, 32))
        format_toolbar.setMovable(False)  # Sets the toolbar as non-movable
        layout.addWidget(format_toolbar)

        self.fonts = QFontComboBox()
        self.fonts.currentFontChanged.connect(self.font_changed)
        format_toolbar.addWidget(self.fonts)

        self.fontsize = QComboBox()
        self.fontsize.addItems([str(s) for s in sizes_of_font])
        self.fontsize.currentIndexChanged.connect(self.font_size_changed)

        format_toolbar.addWidget(self.fontsize)
        format_toolbar.addSeparator()
        bold_icon = QIcon("UI-IMAGES/bold.png")
        italic_icon = QIcon("UI-IMAGES/italic.png")
        underline_icon = QIcon("UI-IMAGES/underline.png")

        self.bold_action = QAction(bold_icon, "Bold", self, checkable=True)
        self.italic_action = QAction(italic_icon, "Italic", self, checkable=True)
        self.underline_action = QAction(
            underline_icon, "Underline", self, checkable=True
        )

        # Add shortcuts to Bold, Italic and Underline Feature
        self.bold_action.setShortcut(QKeySequence.fromString("Ctrl+B"))
        self.italic_action.setShortcut(QKeySequence.fromString("Ctrl+I"))
        self.underline_action.setShortcut(QKeySequence.fromString("Ctrl+U"))

        # To add Bold, Italic and Underline Feature as action
        self.bold_action.toggled.connect(self.set_bold)
        self.italic_action.toggled.connect(self.set_italic)
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

        # Add link action to the toolbar
        self.link_action = QAction("Insert Link", self)
        self.link_action.setIcon(QIcon("UI-IMAGES/link.png"))  # Set your link icon
        self.link_action.triggered.connect(self.show_link_insertion_dialog)
        format_toolbar.addAction(self.link_action)

        # Add the new actions for text highlighting, text color, and bullet points
        highlight_icon = QIcon("UI-IMAGES/highlight.png")
        text_color_icon = QIcon("UI-IMAGES/text-color.png")

        self.highlight_action = QAction(highlight_icon, "Highlight", self)
        self.text_color_action = QAction(text_color_icon, "Text Color", self)

        self.highlight_action.triggered.connect(self.set_highlight)
        self.text_color_action.triggered.connect(self.set_text_color)

        format_toolbar.addActions(
            [self.highlight_action, self.text_color_action]
        )

        self.fonts.setCurrentFont(QFont("Comic Sans MS"))
        self.fontsize.setCurrentIndex(7)

        self.mail_composer.cursorPositionChanged.connect(self.update_formatting_actions)

        # Created Labels for To, Subject, CC, BCC fields
        self.label_for_to = QLabel("To")
        self.to_edit = QLineEdit()
        self.to_edit.setPlaceholderText("Enter the Recipient E-Mail Address(s)")

        # Connect editingFinished signal to clear validation message
        self.to_edit.editingFinished.connect(self.clear_validation_message)

        # Use a timer to set focus to the "To" field after a short delay
        QTimer.singleShot(0, self.AppFocusSetter)
        self.validation_icon = QLabel()

        # Setting the label & icon of validator to "Not Visible" Initially !!!!!
        self.validation_icon.setVisible(False)

        # Create a timer as a class-level attribute
        self.validation_timer = QTimer(self)
        self.validation_timer.setSingleShot(True)  # Set the timer to be single-shot
        self.validation_timer.timeout.connect(self.perform_validation_check)

        # Connect textChanged signal to validate_emails method
        self.to_edit.textChanged.connect(self.validate_email)

        self.label_for_subject = QLabel("Sub")
        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText("Enter the Subject")

        # Connects to the Method "update_title" to update the Window Title
        self.subject_edit.editingFinished.connect(self.update_title)

        self.label_for_cc = QLabel("CC")
        self.cc_edit = QLineEdit()
        self.cc_edit.setPlaceholderText("Enter the CC")

        self.label_for_bcc = QLabel("BCC")
        self.bcc_edit = QLineEdit()
        self.bcc_edit.setPlaceholderText("Enter the BCC")

        # Added buttons and line edits to the respective horizontal layouts

        # For the To Field
        to_layout.addWidget(self.label_for_to)
        to_layout.addWidget(self.to_edit)
        to_layout.addWidget(self.validation_icon)

        # For the Subject Field
        subject_layout.addWidget(self.label_for_subject)
        subject_layout.addWidget(self.subject_edit)

        # For the CC Field
        cc_layout.addWidget(self.label_for_cc)
        cc_layout.addWidget(self.cc_edit)

        # For the BCC Field
        bcc_layout.addWidget(self.label_for_bcc)
        bcc_layout.addWidget(self.bcc_edit)

        # Set fixed width for the Line Edit to make the UI look nice
        button_width = 30
        self.label_for_to.setFixedWidth(button_width)
        self.label_for_cc.setFixedWidth(button_width)
        self.label_for_bcc.setFixedWidth(button_width)
        self.label_for_subject.setFixedWidth(button_width)

        # Add the horizontal layouts to the main vertical layout
        layout.addLayout(to_layout)
        layout.addLayout(cc_layout)
        layout.addLayout(bcc_layout)
        layout.addLayout(subject_layout)

        # Sets the default Font & Font Style
        self.font = QFont(style, 14)
        self.mail_composer.setFont(self.font)
        self.mail_composer.setFontPointSize(14)
        layout.addWidget(self.mail_composer)
        container = QWidget()
        container.setLayout(layout)
        self.setLayout(layout)

        # Created a Heading Layout
        self.heading = QHBoxLayout()

        # Created a Heading Label
        self.heading_label = QLabel("ATTACHMENT CORNER")

        self.heading.addWidget(self.heading_label)
        layout.addLayout(self.heading)

        self.attachment_count_label = QLabel("Attachments: 0")
        self.heading.addWidget(self.attachment_count_label)

        # Create a button for modifying attachments
        modify_button = QPushButton("Modify")
        modify_button.clicked.connect(self.modifyAttachments)
        self.heading.addWidget(modify_button)

        # Add Attachment Button
        self.attach_action = QAction("Attach File", self)
        self.attach_action.setIcon(QIcon("UI-IMAGES/attachment.png"))
        self.attach_action.triggered.connect(self.open_file_dialog)

        # Add the attachment action to the toolbar
        format_toolbar.addAction(self.attach_action)

        # List to store file paths
        self.attachment_paths = []

        # Create a scroll area to display attachment file paths
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        # self.scroll_area.setFixedSize(editor_width, attachment_corner_height)
        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)

        # Add Toggle CC/BCC Action to the toolbar
        self.label_for_cc.setVisible(False)
        self.cc_edit.setVisible(False)
        self.label_for_bcc.setVisible(False)
        self.bcc_edit.setVisible(False)
        self.cc_panel_toggler = QAction("CC", self, checkable=True)
        self.cc_panel_toggler.triggered.connect(self.toggle_cc_bcc_fields)
        format_toolbar.addAction(self.cc_panel_toggler)
        self.bcc_panel_toggler = QAction("BCC", self, checkable=True)
        self.bcc_panel_toggler.triggered.connect(self.toggle_cc_bcc_fields)
        format_toolbar.addAction(self.bcc_panel_toggler)

        self.mode_updater()
        self.update_title()
        self.show()

    def mode_stopper(self, objects, b):
        for o in objects:
            o.blockSignals(b)

    def mode_updater(self):
        self.mode_stopper(
            [self.bold_action, self.italic_action, self.underline_action], True
        )

        cursor = self.mail_composer.textCursor()
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
        cursor = self.mail_composer.textCursor()

        # Preserve existing formatting and only change font size
        char_format = QTextCharFormat()
        char_format.setFontPointSize(size)

        # Apply the modified character format to the selected text
        cursor.mergeCharFormat(char_format)
        self.mail_composer.setTextCursor(cursor)

        self.mail_composer.setFocus()
        self.mode_updater()

    def update_formatting_actions(self):
        cursor = self.mail_composer.textCursor()
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

    def toggle_cc_bcc_fields(self):
        """
        ✨✉️ Manages the smooth appearance and disappearance of the 'CC' and 'BCC' fields,
        ✨  adding a touch of magic to the interface.
        """

        # For handling the "CC" Field
        self.label_for_cc.setVisible(self.cc_panel_toggler.isChecked())
        self.cc_edit.setVisible(self.cc_panel_toggler.isChecked())

        # For handling the "BCC" Field
        self.label_for_bcc.setVisible(self.bcc_panel_toggler.isChecked())
        self.bcc_edit.setVisible(self.bcc_panel_toggler.isChecked())

        # Update layout to reflect changes in visibility
        self.layout().update()
        self.update_title()

    def validate_email(self):
        # Start the timer whenever the text changes
        self.validation_timer.stop()  # Stop the previous timer, if any
        self.validation_timer.start(
            700
        )  # Wait for 0.7 second after the user stops typing

    def perform_validation_check(self):
        emails = self.to_edit.text()

        # Check if the email address is valid
        if check(emails):
            self.to_edit.setStyleSheet(
                """
                    QLineEdit:focus {
                    /* Blue border when the line edit is focused */
                    border: 2px solid #00cc30; 
                    /* White background color when focused */
                    background-color: #FFFFFF;
                    }
                """
            )

            # Show the validation message and icon in a circular tooltip
            tooltip_text = (
                "<div style='background-color:#DDFFDD; padding: 5px; border-radius: 50%; border: 2px solid #cc0000; text-align:center; display: inline-block;'>"
                "<img src='UI-IMAGES/valid.png' width='16' height='16' alt='Icon'>"
                "<font color='green' size = 5><b>Valid</b></font>"
                "</div>"
            )
            QToolTip.showText(
                self.to_edit.mapToGlobal(self.to_edit.rect().bottomLeft()),
                tooltip_text,
            )
        else:
            self.to_edit.setStyleSheet(
                """
                    QLineEdit:focus {
                    /* Blue border when the line edit is focused */
                    border: 2px solid #cc0000;   
                    /* White background color when focused */
                    background-color: #FFFFFF;
                    }
                """
            )
            # Show the validation message and icon in the form of a tooltip
            tooltip_text = (
                "<div style='background-color:#FFDDDD; text-align:center; display: inline-block;'>"
                "<img src='UI-IMAGES/invalid.png' width='16' height='16' alt='Icon'>"
                "<font color='red' size = 4><b>Invalid Data / Format !!!!!</b></font>"
                "</div>"
            )
            QToolTip.showText(
                self.to_edit.mapToGlobal(self.to_edit.rect().bottomLeft()),
                tooltip_text,
            )

        # Start a timer to hide the validation layout after a short delay
        QTimer.singleShot(2000, self.clear_validation_message)

    def clear_validation_message(self):
        # Hide the validation message and icon
        self.to_edit.setStyleSheet(
            """
                    QLineEdit:focus {
                    /* Blue border when the line edit is focused */
                    border: 2px solid #007ACC;  
                    /* White background color when focused */
                    background-color: #FFFFFF;
                    }
                """
        )
        QToolTip.hideText()

    def font_changed(self, font):
        cursor = self.mail_composer.textCursor()
        char_format = cursor.charFormat()

        # Preserve existing formatting properties and only change font family
        char_format.setFontFamily(font.family())

        cursor.mergeCharFormat(char_format)
        self.mail_composer.setTextCursor(cursor)
        self.mail_composer.setFocus()
        self.mode_updater()
        style = self.mail_composer.currentFont().family()

    def font_size_changed(self, index):
        size = float(self.fontsize.itemText(index))
        cursor = self.mail_composer.textCursor()

        # Preserve existing formatting and only change font size
        char_format = QTextCharFormat()
        char_format.setFontPointSize(size)

        # Apply the modified character format to the selected text
        cursor.mergeCharFormat(char_format)
        self.mail_composer.setTextCursor(cursor)

        self.mail_composer.setFocus()
        self.mode_updater()

    def set_bold(self, bold):
        font = self.mail_composer.currentFont()
        font.setBold(bold)
        self.mail_composer.setCurrentFont(font)
        self.mail_composer.setFocus()
        self.mode_updater()

    def set_italic(self, italic):
        font = self.mail_composer.currentFont()
        font.setItalic(italic)
        self.mail_composer.setCurrentFont(font)
        self.mail_composer.setFocus()
        self.mode_updater()

    def set_underline(self, underline):
        font = self.mail_composer.currentFont()
        font.setUnderline(underline)
        self.mail_composer.setCurrentFont(font)
        self.mail_composer.setFocus()
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
        cursor = self.mail_composer.textCursor()
        block_format = cursor.blockFormat()

        # Check if the provided alignment is the same as the current alignment
        if block_format.alignment() == alignment:
            # Set alignment to default left alignment if it's the same as current alignment
            alignment = Qt.AlignmentFlag.AlignLeft

        block_format.setAlignment(alignment)
        cursor.mergeBlockFormat(block_format)
        self.mail_composer.setTextCursor(cursor)
        self.mail_composer.setFocus()
        self.mode_updater()
        self.update_title()

    def set_highlight(self):
        color = QColorDialog.getColor()
        if color.isValid():
            cursor = self.mail_composer.textCursor()
            format = QTextCharFormat()
            format.setBackground(color)
            cursor.mergeCharFormat(format)

    def set_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            cursor = self.mail_composer.textCursor()
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
                cursor.setCharFormat(format)  # Apply the format to the current position as well

            self.mail_composer.setTextCursor(cursor)


    def update_title(self):
        title = self.subject_edit.text()

        if title == "":
            self.setWindowTitle("New Message")
        else:
            self.setWindowTitle(title)

    def AppFocusSetter(self):
        """
        This method sets Focus to the "To" Field, making it ready for user input ASAP
        """
        self.to_edit.setFocus()

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

    def update_attachment_list(self):
        # Clear existing items
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Add new attachment items and update attachment count
        for path in self.attachment_paths:
            file_extension = os.path.splitext(path)[0]
            label = QLabel(path)
            # Get file extension and fetch corresponding icon
            self.scroll_layout.addWidget(label)

        # Update attachment count label
        self.attachment_count_label.setText(
            f"Attachments: {len(self.attachment_paths)}"
        )

    def modifyAttachments(self):
        # Create a modification window with current attachment paths
        modify_window = ModifyAttachmentWindow(self.attachment_paths)
        modify_window.exec()  # Use exec_() to make it a modal window

        # Update attachment_paths based on the modified list
        self.attachment_paths = modify_window.attachment_paths

        # Update attachment list in the UI
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
        cursor = self.mail_composer.textCursor()
        cursor.insertHtml(link_html)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            event.ignore()  # Ignore the Enter/Return key press
        elif (
            event.key() == Qt.Key.Key_W
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            print("Closed")
            self.close()
        else:
            super().keyPressEvent(event)

        if event.key() == Qt.Key.Key_Return:
            cursor = self.textCursor()
            current_list = cursor.currentList()
            if current_list:
                if cursor.atBlockStart():
                    cursor.currentList().remove(cursor.block())
                    self.setTextCursor(cursor)
                    return
            super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    main()
