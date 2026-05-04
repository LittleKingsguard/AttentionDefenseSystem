import sys
from typing import Optional, Dict
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QTextEdit, QPushButton, QFrame, QGraphicsDropShadowEffect, QScrollArea, QComboBox, QLineEdit
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QColor
from db import get_logs, get_vector_store, get_filter_options

class ApprovalWindow(QWidget):
    def __init__(self, requester: str, incoming_message: str, drafted_response: str):
        super().__init__()
        self.result: Optional[Dict[str, str]] = None
        self.drafted_response = drafted_response
        
        self.setWindowTitle("Attention Defense System")
        self.setFixedSize(800, 680)
        # Frameless window for premium popup feel
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.init_ui(requester, incoming_message)
        self.animate_window()

    def init_ui(self, requester: str, incoming_message: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Main container with rounded corners and shadow
        self.container = QFrame(self)
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            #container {
                background-color: #1E1E1E;
                border-radius: 15px;
                border: 1px solid #333333;
            }
        """)
        
        # Add drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { 
                border: none;
                background-color: transparent;
            }
            QTabBar::tab {
                background: #2B2B2B;
                color: #888888;
                padding: 10px 25px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 5px;
                font-family: Inter, Arial;
                font-weight: bold;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background: #3B3B3B;
                color: #FFFFFF;
            }
        """)
        
        # Tab 1: Current Request
        self.tab_current = QWidget()
        self.init_current_tab(self.tab_current, requester, incoming_message)
        self.tabs.addTab(self.tab_current, "Current Request")
        
        # Tab 2: History
        self.tab_history = QWidget()
        self.init_history_tab(self.tab_history)
        self.tabs.addTab(self.tab_history, "History")
        
        # Tab 3: Search Knowledge Base
        self.tab_search = QWidget()
        self.init_search_tab(self.tab_search)
        self.tabs.addTab(self.tab_search, "Search Knowledge Base")
        
        container_layout.addWidget(self.tabs)
        layout.addWidget(self.container)

    def init_current_tab(self, parent_widget, requester, incoming_message):
        current_layout = QVBoxLayout(parent_widget)
        current_layout.setContentsMargins(10, 20, 10, 10)
        current_layout.setSpacing(20)

        # Header
        header = QLabel("Agent Drafted a Response")
        header.setStyleSheet("color: #FFFFFF; font-size: 24px; font-weight: bold; font-family: Inter, Arial;")
        current_layout.addWidget(header)

        # Context box
        context_frame = QFrame()
        context_frame.setStyleSheet("""
            QFrame {
                background-color: #2B2B2B;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        context_layout = QVBoxLayout(context_frame)
        
        lbl_from = QLabel(f"From: {requester}")
        lbl_from.setStyleSheet("color: #E0E0E0; font-size: 15px; font-weight: bold; font-family: Inter, Arial;")
        context_layout.addWidget(lbl_from)
        
        lbl_msg = QLabel(f"Message: {incoming_message}")
        lbl_msg.setWordWrap(True)
        lbl_msg.setStyleSheet("color: #CCCCCC; font-size: 14px; font-family: Inter, Arial;")
        context_layout.addWidget(lbl_msg)
        
        current_layout.addWidget(context_frame)

        # Draft label
        draft_lbl = QLabel("Proposed Status Update (Feel free to edit):")
        draft_lbl.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: bold; font-family: Inter, Arial;")
        current_layout.addWidget(draft_lbl)

        # Text Editor
        self.textbox = QTextEdit()
        self.textbox.setPlainText(self.drafted_response)
        self.textbox.setStyleSheet("""
            QTextEdit {
                background-color: #121212;
                color: #FFFFFF;
                border: 2px solid #3B3B3B;
                border-radius: 10px;
                padding: 10px;
                font-size: 15px;
                font-family: Inter, Arial;
            }
            QTextEdit:focus {
                border: 2px solid #5C6BC0;
            }
        """)
        current_layout.addWidget(self.textbox)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        btn_approve = QPushButton("Approve & Send")
        btn_approve.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_approve.setStyleSheet(self.get_btn_style("#2E7D32", "#1B5E20"))
        btn_approve.clicked.connect(self.on_approve)
        
        btn_edit = QPushButton("Send Edited")
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet(self.get_btn_style("#1565C0", "#0D47A1"))
        btn_edit.clicked.connect(self.on_edit)
        
        btn_reject = QPushButton("Reject")
        btn_reject.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reject.setStyleSheet(self.get_btn_style("#C62828", "#b71c1c"))
        btn_reject.clicked.connect(self.on_reject)

        btn_layout.addWidget(btn_approve)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_reject)
        
        current_layout.addLayout(btn_layout)

    def init_history_tab(self, parent_widget):
        layout = QVBoxLayout(parent_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        header = QLabel("Interaction History")
        header.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: bold; font-family: Inter, Arial;")
        layout.addWidget(header)
        
        # --- Filters Area ---
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        self.filter_dir = QComboBox()
        self.filter_dir.addItems(["All Directions", "Sent", "Received"])
        self.filter_dir.setStyleSheet(self.get_combo_style())
        self.filter_dir.currentTextChanged.connect(self.refresh_history)
        
        self.filter_topic = QComboBox()
        self.filter_topic.addItem("All Topics")
        self.filter_topic.setStyleSheet(self.get_combo_style())
        self.filter_topic.currentTextChanged.connect(self.refresh_history)
        
        self.filter_party = QComboBox()
        self.filter_party.addItem("All Parties")
        self.filter_party.setStyleSheet(self.get_combo_style())
        self.filter_party.currentTextChanged.connect(self.refresh_history)
        
        filter_layout.addWidget(self.filter_dir)
        filter_layout.addWidget(self.filter_topic)
        filter_layout.addWidget(self.filter_party)
        layout.addLayout(filter_layout)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical {
                border: none;
                background: #1E1E1E;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                min-height: 20px;
                border-radius: 5px;
            }
        """)
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setSpacing(15)
        
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)
        
        self.scroll.verticalScrollBar().valueChanged.connect(self.on_scroll)
        
        self.history_offset = 0
        self.history_limit = 100
        self.is_loading_history = False
        
        self.load_history_data()
        self.refresh_history()

    def get_combo_style(self):
        return """
            QComboBox {
                background-color: #2B2B2B;
                color: #FFFFFF;
                border: 1px solid #3B3B3B;
                border-radius: 5px;
                padding: 5px 10px;
                font-family: Inter, Arial;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #2B2B2B;
                color: #FFFFFF;
                selection-background-color: #3B3B3B;
            }
        """

    def load_history_data(self):
        topics, parties = get_filter_options()
        
        self.filter_topic.blockSignals(True)
        self.filter_party.blockSignals(True)
        
        self.filter_topic.clear()
        self.filter_topic.addItem("All Topics")
        self.filter_topic.addItems(topics)
        
        self.filter_party.clear()
        self.filter_party.addItem("All Parties")
        self.filter_party.addItems(parties)
        
        self.filter_topic.blockSignals(False)
        self.filter_party.blockSignals(False)

    def refresh_history(self):
        self.history_offset = 0
        self.load_more_history(clear=True)
        
    def load_more_history(self, clear=False):
        if self.is_loading_history: return
        self.is_loading_history = True
        
        f_dir = self.filter_dir.currentText()
        f_topic = self.filter_topic.currentText()
        f_party = self.filter_party.currentText()
        
        new_logs = get_logs(limit=self.history_limit, offset=self.history_offset, direction=f_dir, topic=f_topic, party=f_party)
        
        if clear:
            while self.scroll_layout.count():
                child = self.scroll_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                    
            if not new_logs:
                lbl = QLabel("No messages match the current filters.")
                lbl.setStyleSheet("color: #888888; font-size: 15px; font-style: italic; font-family: Inter, Arial;")
                self.scroll_layout.addWidget(lbl)
                self.is_loading_history = False
                return

        for log in new_logs:
            frame = QFrame()
            frame.setStyleSheet("QFrame { background-color: #2B2B2B; border-radius: 8px; border: 1px solid #3B3B3B; }")
            flayout = QVBoxLayout(frame)
            
            # Top Row: Direction, Topic, Timestamp
            top_layout = QHBoxLayout()
            direction = log.get('direction', 'unknown').upper()
            dir_color = "#4CAF50" if direction == 'SENT' else "#2196F3"
            dir_lbl = QLabel(f"<b>{direction}</b>")
            dir_lbl.setStyleSheet(f"color: {dir_color}; font-size: 12px;")
            
            topic_lbl = QLabel(f"Topic: {log.get('topic', 'General')}")
            topic_lbl.setStyleSheet("color: #AAAAAA; font-size: 12px; margin-left: 10px;")
            
            time_str = log.get('timestamp', '')[:16].replace('T', ' ')
            time_lbl = QLabel(time_str)
            time_lbl.setStyleSheet("color: #888888; font-size: 12px;")
            
            top_layout.addWidget(dir_lbl)
            top_layout.addWidget(topic_lbl)
            top_layout.addStretch()
            top_layout.addWidget(time_lbl)
            flayout.addLayout(top_layout)
            
            # Party
            party = log.get('party', 'Unknown')
            party_lbl = QLabel(f"<b>Party:</b> {party}")
            party_lbl.setStyleSheet("color: #E0E0E0; font-size: 14px; font-family: Inter, Arial;")
            flayout.addWidget(party_lbl)
            
            # Content
            if log.get('content'):
                cont_lbl = QLabel(log.get('content'))
                cont_lbl.setWordWrap(True)
                cont_lbl.setStyleSheet("color: #FFFFFF; font-size: 14px; font-family: Inter, Arial; margin-top: 5px;")
                flayout.addWidget(cont_lbl)
                
            self.scroll_layout.addWidget(frame)
            
        self.history_offset += len(new_logs)
        self.is_loading_history = False

    def on_scroll(self, value):
        # Allow loading more if we have reached the bottom
        if value == self.scroll.verticalScrollBar().maximum():
            self.load_more_history()

    def init_search_tab(self, parent_widget):
        layout = QVBoxLayout(parent_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        header = QLabel("Search Knowledge Base")
        header.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: bold; font-family: Inter, Arial;")
        layout.addWidget(header)
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter query (e.g., 'Ticket-404', 'latest commits')...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2B2B2B;
                color: #FFFFFF;
                border: 1px solid #3B3B3B;
                border-radius: 5px;
                padding: 10px;
                font-family: Inter, Arial;
                font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #5C6BC0; }
        """)
        self.search_input.returnPressed.connect(self.perform_search)
        
        search_btn = QPushButton("Search")
        search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        search_btn.setStyleSheet(self.get_btn_style("#1565C0", "#0D47A1"))
        search_btn.clicked.connect(self.perform_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        self.search_scroll = QScrollArea()
        self.search_scroll.setWidgetResizable(True)
        self.search_scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical {
                border: none;
                background: #1E1E1E;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                min-height: 20px;
                border-radius: 5px;
            }
        """)
        
        self.search_scroll_content = QWidget()
        self.search_scroll_content.setStyleSheet("background-color: transparent;")
        self.search_scroll_layout = QVBoxLayout(self.search_scroll_content)
        self.search_scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.search_scroll_layout.setSpacing(15)
        
        self.search_scroll.setWidget(self.search_scroll_content)
        layout.addWidget(self.search_scroll)
        
    def perform_search(self):
        query = self.search_input.text().strip()
        if not query: return
        
        while self.search_scroll_layout.count():
            child = self.search_scroll_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            
        try:
            vs = get_vector_store()
            docs = vs.similarity_search(query, k=5)
        except Exception as e:
            err_lbl = QLabel(f"Error querying database: {e}")
            err_lbl.setStyleSheet("color: #F44336; font-size: 14px;")
            self.search_scroll_layout.addWidget(err_lbl)
            return
            
        if not docs:
            lbl = QLabel("No documents found matching the query.")
            lbl.setStyleSheet("color: #888888; font-size: 15px; font-style: italic;")
            self.search_scroll_layout.addWidget(lbl)
        else:
            for d in docs:
                frame = QFrame()
                frame.setStyleSheet("QFrame { background-color: #2B2B2B; border-radius: 8px; border: 1px solid #3B3B3B; }")
                flayout = QVBoxLayout(frame)
                
                source = d.metadata.get('source', 'Unknown Source')
                src_lbl = QLabel(f"<b>Source:</b> {source}")
                src_lbl.setStyleSheet("color: #4CAF50; font-size: 13px; font-family: Inter, Arial;")
                flayout.addWidget(src_lbl)
                
                cont_lbl = QLabel(d.page_content)
                cont_lbl.setWordWrap(True)
                cont_lbl.setStyleSheet("color: #FFFFFF; font-size: 14px; font-family: Inter, Arial;")
                flayout.addWidget(cont_lbl)
                
                self.search_scroll_layout.addWidget(frame)

    def get_btn_style(self, bg_color, hover_color):
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 15px;
                font-weight: bold;
                font-family: Inter, Arial;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """

    def animate_window(self):
        # Micro-animation for slide up
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(400)
        self.animation.setEasingCurve(QEasingCurve.Type.OutBack)
        
        # Center on screen and slide up
        screen_geo = QApplication.primaryScreen().geometry()
        x = (screen_geo.width() - self.width()) // 2
        y = (screen_geo.height() - self.height()) // 2
        
        self.animation.setStartValue(QRect(x, y + 50, self.width(), self.height()))
        self.animation.setEndValue(QRect(x, y, self.width(), self.height()))
        self.animation.start()

    def on_approve(self):
        self.result = {"action": "approve", "content": self.textbox.toPlainText().strip()}
        self.close()

    def on_edit(self):
        self.result = {"action": "edit", "content": self.textbox.toPlainText().strip()}
        self.close()

    def on_reject(self):
        self.result = {"action": "reject", "content": None}
        self.close()

def request_human_approval(requester: str, incoming_message: str, drafted_response: str) -> Optional[Dict[str, str]]:
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    window = ApprovalWindow(requester, incoming_message, drafted_response)
    window.show()
    app.exec()
    return window.result
