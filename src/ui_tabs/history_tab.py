from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QComboBox
from PyQt6.QtCore import Qt
from db import get_logs, get_filter_options
from .styles import get_combo_style

class HistoryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.history_offset = 0
        self.history_limit = 100
        self.is_loading_history = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        header = QLabel("Interaction History")
        header.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: bold; font-family: Inter, Arial;")
        layout.addWidget(header)
        
        # Filters Area
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        self.filter_dir = QComboBox()
        self.filter_dir.addItems(["All Directions", "Sent", "Received"])
        self.filter_dir.setStyleSheet(get_combo_style())
        self.filter_dir.currentTextChanged.connect(self.refresh_history)
        
        self.filter_topic = QComboBox()
        self.filter_topic.addItem("All Topics")
        self.filter_topic.setStyleSheet(get_combo_style())
        self.filter_topic.currentTextChanged.connect(self.refresh_history)
        
        self.filter_party = QComboBox()
        self.filter_party.addItem("All Parties")
        self.filter_party.setStyleSheet(get_combo_style())
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
        
        self.load_history_data()
        self.refresh_history()

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
            
            party = log.get('party', 'Unknown')
            party_lbl = QLabel(f"<b>Party:</b> {party}")
            party_lbl.setStyleSheet("color: #E0E0E0; font-size: 14px; font-family: Inter, Arial;")
            flayout.addWidget(party_lbl)
            
            if log.get('content'):
                cont_lbl = QLabel(log.get('content'))
                cont_lbl.setWordWrap(True)
                cont_lbl.setStyleSheet("color: #FFFFFF; font-size: 14px; font-family: Inter, Arial; margin-top: 5px;")
                flayout.addWidget(cont_lbl)
                
            self.scroll_layout.addWidget(frame)
            
        self.history_offset += len(new_logs)
        self.is_loading_history = False

    def on_scroll(self, value):
        if value == self.scroll.verticalScrollBar().maximum():
            self.load_more_history()
