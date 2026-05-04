from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QFrame
from PyQt6.QtCore import Qt
from db import get_vector_store
from .styles import get_btn_style

class SearchTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
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
        search_btn.setStyleSheet(get_btn_style("#1565C0", "#0D47A1"))
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
