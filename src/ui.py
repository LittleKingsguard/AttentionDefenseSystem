import sys
from typing import Optional, Dict
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QColor

# Import extracted UI tabs
from ui_tabs.current_request_tab import CurrentRequestTab
from ui_tabs.history_tab import HistoryTab
from ui_tabs.search_tab import SearchTab
from ui_tabs.settings_tab import SettingsTab

class ApprovalWindow(QWidget):
    def __init__(self, requester: str, incoming_message: str, drafted_response: str):
        super().__init__()
        self.result: Optional[Dict[str, str]] = None
        
        self.setWindowTitle("Attention Defense System")
        self.setFixedSize(800, 680)
        # Frameless window for premium popup feel
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.init_ui(requester, incoming_message, drafted_response)
        self.animate_window()

    def init_ui(self, requester: str, incoming_message: str, drafted_response: str):
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
        self.tab_current = CurrentRequestTab(requester, incoming_message, drafted_response)
        self.tab_current.action_taken.connect(self.on_action_taken)
        self.tabs.addTab(self.tab_current, "Current Request")
        
        # Tab 2: History
        self.tab_history = HistoryTab()
        self.tabs.addTab(self.tab_history, "History")
        
        # Tab 3: Search Knowledge Base
        self.tab_search = SearchTab()
        self.tabs.addTab(self.tab_search, "Search Knowledge Base")
        
        # Tab 4: Settings
        self.tab_settings = SettingsTab()
        self.tabs.addTab(self.tab_settings, "Settings")
        
        container_layout.addWidget(self.tabs)
        layout.addWidget(self.container)

    def on_action_taken(self, result: dict):
        self.result = result
        self.close()

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

def request_human_approval(requester: str, incoming_message: str, drafted_response: str) -> Optional[Dict[str, str]]:
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    window = ApprovalWindow(requester, incoming_message, drafted_response)
    window.show()
    app.exec()
    return window.result
