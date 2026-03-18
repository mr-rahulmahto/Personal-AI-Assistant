from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStackedWidget,
                             QWidget, QLineEdit, QVBoxLayout, QHBoxLayout,
                             QPushButton, QFrame, QLabel, QSizePolicy)
from PyQt5.QtGui import (QIcon, QMovie, QTextCharFormat, QColor, QFont,
                         QPixmap, QTextBlockFormat, QPainter)
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Jarvis")
current_dir = os.getcwd()
old_chat_message = " "
TempDirPath    = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"


# Utility helpers


def AnswerModifier(Answer):
    lines = Answer.split('\n')
    return '\n'.join(line for line in lines if line.strip())


def QueryModifier(Query):
    new_query = Query.lower().strip()
    if not new_query:
        return ""
    question_words = ["how","what","where","which","when",
                      "why","whose","whom","can you","what's","how's"]
    punctuation = "?" if any(new_query.startswith(w) for w in question_words) else "."
    if new_query[-1] in ".?!":
        new_query = new_query[:-1] + punctuation
    else:
        new_query += punctuation
    return new_query.capitalize()


def SetMicrophoneStatus(Command):
    with open(rf'{TempDirPath}\Mic.data', "w", encoding='utf-8') as f:
        f.write(Command)

def GetMicrophoneStatus():
    with open(rf'{TempDirPath}\Mic.data', "r", encoding='utf-8') as f:
        return f.read().strip()

def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data', "w", encoding='utf-8') as f:
        f.write(Status)

def GetAssistantStatus():
    try:
        with open(rf'{TempDirPath}\Status.data', "r", encoding='utf-8') as f:
            return f.read()
    except:
        return "Mic off"

def MicButtonInitialed():
    SetMicrophoneStatus("True")
    SetAssistantStatus("Listening...")

def MicButtonClosed():
    SetMicrophoneStatus("False")
    SetAssistantStatus("Mic off")

def GraphicsDirectoryPath(Filename):
    return rf'{GraphicsDirPath}\{Filename}'

def TempDirectoryPath(Filename):
    return rf'{TempDirPath}\{Filename}'

def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Responses.data', "w", encoding='utf-8') as f:
        f.write(Text)



# Shared mic state  (one global flag, both screens stay in sync)


mic_is_on = False

def toggle_icon(instance, event=None):
    global mic_is_on
    mic_is_on = not mic_is_on
    if mic_is_on:
        instance.load_icon(GraphicsDirectoryPath('Mice_on.png'), 60, 60)
        MicButtonInitialed()
    else:
        instance.load_icon(GraphicsDirectoryPath('Mice_off.png'), 60, 60)
        MicButtonClosed()

def sync_icon(instance):
    if mic_is_on:
        instance.load_icon(GraphicsDirectoryPath('Mice_on.png'), 60, 60)
    else:
        instance.load_icon(GraphicsDirectoryPath('Mice_off.png'), 60, 60)



# Reusable styled input bar  (shared by both screens)


INPUT_STYLE = """
QLineEdit {
    background-color: #111;
    color: #e8e8e8;
    border: 1px solid #333;
    border-radius: 22px;
    padding: 0px 20px;
    font-size: 14px;
    selection-background-color: #444;
}
QLineEdit:focus {
    border: 1px solid #666;
    background-color: #1a1a1a;
}
"""

SEND_STYLE = """
QPushButton {
    background-color: #1e1e1e;
    color: #ccc;
    border: 1px solid #444;
    border-radius: 22px;
    font-size: 15px;
    font-weight: bold;
}
QPushButton:hover   { background-color: #2e2e2e; color: white; border-color: #777; }
QPushButton:pressed { background-color: #444;    color: white; }
"""


def make_input_row(send_callback):
    """
    Returns (row_widget, input_box) — a fully styled input bar.
    send_callback is called when Enter is pressed or Send clicked.
    """
    row = QWidget()
    row.setStyleSheet("background: transparent;")
    h = QHBoxLayout(row)
    h.setContentsMargins(10, 6, 10, 10)
    h.setSpacing(8)

    box = QLineEdit()
    box.setPlaceholderText("  Type a message or use the mic…")
    box.setFixedHeight(44)
    box.setStyleSheet(INPUT_STYLE)
    box.returnPressed.connect(send_callback)

    btn = QPushButton("➤")
    btn.setFixedSize(44, 44)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet(SEND_STYLE)
    btn.clicked.connect(send_callback)

    h.addWidget(box)
    h.addWidget(btn)
    return row, box



# ChatSection 


class ChatSection(QWidget):

    def __init__(self):
        super().__init__()
        self.old_spoken_text = ""

        # Expand to fill whatever space the parent gives it
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ── root layout ───
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setLayout(root)

        # ── chat display ──────
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        f = QFont()
        f.setPointSize(13)
        self.chat_text_edit.setFont(f)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(Qt.white))
        self.chat_text_edit.setCurrentCharFormat(fmt)
        self.chat_text_edit.viewport().installEventFilter(self)
        root.addWidget(self.chat_text_edit, stretch=1)

        # ── bottom area:
        bottom = QWidget()
        bottom.setStyleSheet("background: transparent;")
        bottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        blay = QVBoxLayout(bottom)
        blay.setContentsMargins(0, 0, 0, 0)
        blay.setSpacing(2)

        # gif + mic row
        gif_mic_row = QHBoxLayout()
        gif_mic_row.setContentsMargins(10, 0, 10, 0)
        gif_mic_row.setSpacing(10)

        # mic button
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(60, 60)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setCursor(Qt.PointingHandCursor)
        self.icon_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 1px solid #444;
                border-radius: 30px;
            }
            QLabel:hover { background-color: #2a2a2a; border-color: #888; }
        """)
        sync_icon(self)
        self.icon_label.mousePressEvent = lambda e: toggle_icon(self, e)

        # gif
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none; background: transparent;")
        movie = QMovie(GraphicsDirectoryPath('JarvisAi.gif'))
        movie.setScaledSize(QSize(320, 180))
        self.gif_label.setMovie(movie)
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        movie.start()

        gif_mic_row.addWidget(self.icon_label, alignment=Qt.AlignLeft | Qt.AlignBottom)
        gif_mic_row.addStretch()
        gif_mic_row.addWidget(self.gif_label, alignment=Qt.AlignRight | Qt.AlignBottom)
        blay.addLayout(gif_mic_row)

        # status label
        self.label = QLabel(" ")
        self.label.setStyleSheet(
            "color:#888; font-size:13px; border:none; background:transparent;"
            "padding-right:14px;"
        )
        self.label.setAlignment(Qt.AlignRight)
        blay.addWidget(self.label)

        # input bar
        input_row, self.input_box = make_input_row(self.sendMessage)
        blay.addWidget(input_row)

        root.addWidget(bottom)

        # ── scrollbar style ────
        self.setStyleSheet("""
            QWidget { background-color: black; }
            QScrollBar:vertical {
                border: none; background: #0d0d0d; width: 6px; margin: 0;
            }
            QScrollBar::handle:vertical { background: #333; min-height: 20px; border-radius:3px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)

        # ── timer ────
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        # self.timer.timeout.connect(self.loadSpokenText)
        self.timer.start(100)

    def showEvent(self, event):
        super().showEvent(event)
        sync_icon(self)

    # ── send typed message ─
    def sendMessage(self):
        text = self.input_box.text().strip()
        if not text:
            return
        # self.addMessage(f"You: {text}", "#00BFFF")  
        try:
            with open(TempDirectoryPath("Queries.data"), "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            print("Query write error:", e)
        self.input_box.clear()
        self.input_box.setFocus()

    # ── spoken text from mic ────────────  # Already Add the ChatBot AI
    # def loadSpokenText(self):
    #     try:
    #         path = TempDirectoryPath("Spoken.data")
    #         if not os.path.exists(path):
    #             return
    #         with open(path, "r", encoding="utf-8") as f:
    #             spoken = f.read().strip()
    #         if not spoken or spoken == self.old_spoken_text:
    #             return
    #         self.old_spoken_text = spoken
    #         self.addMessage(f"{Assistantname}: {spoken}", "#00BFFF")
    #         with open(path, "w", encoding="utf-8") as f:
    #             f.write("")
    #     except Exception as e:
    #         print("Spoken load error:", e)

    # ── AI responses ──────────────
    def loadMessages(self):
        global old_chat_message
        try:
            with open(TempDirectoryPath("Responses.data"), "r", encoding="utf-8") as f:
                messages = f.read()
            if not messages or len(messages) <= 1:
                return
            if old_chat_message == messages:
                return
            self.addMessage(f"{messages}", "white")  #Also add Assistantname but Not Add its Main.py file alredy add it
            old_chat_message = messages
        except Exception as e:
            print("Message load error:", e)

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding="utf-8") as f:
                self.label.setText(f.read())
        except Exception as e:
            print("Status read error:", e)

    def load_icon(self, path, width=60, height=60):
        self.icon_label.setPixmap(QPixmap(path).scaled(
            width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        fmt      = QTextCharFormat()
        fmt_block = QTextBlockFormat()
        fmt_block.setTopMargin(8)
        fmt_block.setLeftMargin(12)
        fmt.setForeground(QColor(color))
        cursor.setCharFormat(fmt)
        cursor.setBlockFormat(fmt_block)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)
        self.chat_text_edit.verticalScrollBar().setValue(
         self.chat_text_edit.verticalScrollBar().maximum())



# InitialScreen  —


class InitialScreen(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.old_spoken_text = ""
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setLayout(root)

        # ── full-width GIF ────
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none; background: black;")
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # movie scaled later in resizeEvent
        self.movie = QMovie(GraphicsDirectoryPath('JarvisAi.gif'))
        self.gif_label.setMovie(self.movie)
        self.movie.start()
        root.addWidget(self.gif_label)

        # ── bottom panel ──
        bottom = QWidget()
        bottom.setStyleSheet("background: black;")
        bottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        blay = QVBoxLayout(bottom)
        blay.setContentsMargins(0, 4, 0, 0)
        blay.setSpacing(2)

        # status label
        self.label = QLabel("")
        self.label.setStyleSheet(
            "color: #888; font-size: 14px; background: transparent; "
            "border: none; padding: 0 16px;"
        )
        self.label.setAlignment(Qt.AlignCenter)
        blay.addWidget(self.label)

        # mic + input row
        ctrl_row = QHBoxLayout()
        ctrl_row.setContentsMargins(10, 4, 10, 10)
        ctrl_row.setSpacing(10)

        # mic button
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(60, 60)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setCursor(Qt.PointingHandCursor)
        self.icon_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 1px solid #444;
                border-radius: 30px;
            }
            QLabel:hover { background-color: #2a2a2a; border-color: #888; }
        """)
        sync_icon(self)
        self.icon_label.mousePressEvent = lambda e: toggle_icon(self, e)

        # input + send
        input_widget = QWidget()
        input_widget.setStyleSheet("background: transparent;")
        input_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        ih = QHBoxLayout(input_widget)
        ih.setContentsMargins(0, 0, 0, 0)
        ih.setSpacing(8)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("  Type a message or use the mic…")
        self.input_box.setFixedHeight(44)
        self.input_box.setStyleSheet(INPUT_STYLE)
        self.input_box.returnPressed.connect(self.sendMessage)

        send_btn = QPushButton("➤")
        send_btn.setFixedSize(44, 44)
        send_btn.setCursor(Qt.PointingHandCursor)
        send_btn.setStyleSheet(SEND_STYLE)
        send_btn.clicked.connect(self.sendMessage)

        ih.addWidget(self.input_box)
        ih.addWidget(send_btn)

        ctrl_row.addWidget(self.icon_label, alignment=Qt.AlignVCenter)
        ctrl_row.addWidget(input_widget)
        blay.addLayout(ctrl_row)

        root.addWidget(bottom)

        self.setStyleSheet("background-color: black;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.timeout.connect(self.loadSpokenText)
        self.timer.start(100)

    def resizeEvent(self, event):
        """Scale GIF to match window width."""
        super().resizeEvent(event)
        w = self.width()
        h = int(w / 13 * 7)
        self.movie.setScaledSize(QSize(w, h))

    def showEvent(self, event):
        super().showEvent(event)
        sync_icon(self)

    def sendMessage(self):
        text = self.input_box.text().strip()
        if not text:
            return
        try:
            with open(TempDirectoryPath("Queries.data"), "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            print("Query write error:", e)
        self.input_box.clear()
        self.input_box.setFocus()

    def loadSpokenText(self):
        try:
            path = TempDirectoryPath("Spoken.data")
            if not os.path.exists(path):
                return
            with open(path, "r", encoding="utf-8") as f:
                spoken = f.read().strip()
            if not spoken or spoken == self.old_spoken_text:
                return
            self.old_spoken_text = spoken
            # Show spoken text in status label briefly
            self.label.setText(f"You said: {spoken}")
            with open(path, "w", encoding="utf-8") as f:
                f.write("")
        except Exception as e:
            print("Spoken load error:", e)

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), 'r', encoding='utf-8') as f:
                self.label.setText(f.read())
        except Exception as e:
            print("Status read error:", e)

    def load_icon(self, path, width=60, height=60):
        self.icon_label.setPixmap(QPixmap(path).scaled(
            width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation))



# MessageScreen  


class MessageScreen(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(ChatSection())
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")



# CustomerTopBar


class CustomerTopBar(QWidget):

    def __init__(self, parent=None, stacked_widget=None):
        super().__init__(parent)
        self.current_screen  = None
        self.stacked_widget  = stacked_widget
        self.draggable = True
        self.offset    = None
        self.normal_geometry = None  # store restore geometry
        self._initUI()

    def _initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(8)

        # Title: allow it to expand but not steal all space
        title = QLabel(f"{str(Assistantname).capitalize()} AI")
        title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        title.setMinimumWidth(160)
        title.setStyleSheet(
            "color:black; font-size:18px; font-weight:600; background:white; padding-left:6px;"
        )
        title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.title = title  # expose for mouse double-click

        def nav_btn(text, icon_file):
            b = QPushButton(text)
            b.setIcon(QIcon(GraphicsDirectoryPath(icon_file)))
            # make sure nav buttons keep a readable width
            b.setMinimumWidth(88)
            b.setMaximumHeight(36)
            b.setIconSize(QSize(18, 18))
            b.setStyleSheet(
                "height:36px; padding:0 12px; background:white; color:black; "
                "border:none; font-size:13px; border-radius:4px;"
            )
            b.setCursor(Qt.PointingHandCursor)
            return b

        def win_btn(icon_file, size=20):
            b = QPushButton()
            b.setIcon(QIcon(GraphicsDirectoryPath(icon_file)))
            b.setIconSize(QSize(size, size))
            b.setFixedSize(40, 40)
            b.setFlat(True)
            b.setStyleSheet(
                "background:white; border:none; border-radius:6px;"
                "QPushButton:hover{background:#e0e0e0;}"
            )
            b.setCursor(Qt.PointingHandCursor)
            return b

        home_btn    = nav_btn("Home",  "home.png")
        message_btn = nav_btn("Chats", "chat.png")
        min_btn     = win_btn("Minimize2-icon.png", size=18)
        self.max_btn = win_btn("Maximize-icon.png", size=18)
        close_btn   = win_btn("close.png", size=18)

        self.maximize_icon = QIcon(GraphicsDirectoryPath('Maximize-icon.png'))
        self.restore_icon  = QIcon(GraphicsDirectoryPath('Minimize-icon.png'))

        # Connect actions
        home_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        min_btn.clicked.connect(self.minimizeWindow)
        self.max_btn.clicked.connect(self.maximizeWindow)
        close_btn.clicked.connect(self.closeWindow)

        # Build layout
        layout.addWidget(title)
        layout.addStretch(1)
        layout.addWidget(home_btn)
        layout.addWidget(message_btn)
        layout.addStretch(1)
        layout.addWidget(min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(close_btn)

        # Ensure parent window has reasonable min/max so icons are visible
        parent = self.parent()
        if parent:
            screen = QApplication.primaryScreen()
            screen_rect = screen.availableGeometry()
            parent.setMinimumSize(900, 600)
            parent.setMaximumSize(screen_rect.width(), screen_rect.height())

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.window().showMinimized()

    def closeWindow(self):
        self.window().close()

    def maximizeWindow(self):
        w = self.window()
        screen = QApplication.primaryScreen()
        avail = screen.availableGeometry()

        # If currently maximized (we saved normal_geometry), restore
        if w.isMaximized() or getattr(self, "is_maximized", False):
            if self.normal_geometry:
                w.setGeometry(self.normal_geometry)
            else:
                w.showNormal()
            self.max_btn.setIcon(self.maximize_icon)
            self.is_maximized = False
        else:
            # store normal geometry so we can restore later
            self.normal_geometry = w.geometry()
            w.setGeometry(avail)   
            self.max_btn.setIcon(self.restore_icon)
            self.is_maximized = True

    def mouseDoubleClickEvent(self, event):
        self.maximizeWindow()
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if self.draggable and event.button() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset and event.buttons() & Qt.LeftButton:
            # Move top-level window (works with frameless)
            self.window().move(event.globalPos() - self.offset)



# MainWindow


class MainWindow(QMainWindow):
    
    screen = QApplication.primaryScreen()


 

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self._initUI()


    def _initUI(self):
        # Use modern screen API
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # Set window size properly (NOT forced fullscreen)
        self.resize(int(screen_geometry.width() * 0.85),
                    int(screen_geometry.height() * 0.85))

        # Center window
        self.move(
            (screen_geometry.width() - self.width()) // 2,
            (screen_geometry.height() - self.height()) // 2
        )

        self.stacked_widget = QStackedWidget(self)
        self.initial_screen = InitialScreen()
        self.message_screen = MessageScreen()

        self.stacked_widget.addWidget(self.initial_screen)
        self.stacked_widget.addWidget(self.message_screen)

        self.setStyleSheet("background-color: black;")

        top_bar = CustomerTopBar(self, self.stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(self.stacked_widget)



# Entry point


def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    GraphicalUserInterface()