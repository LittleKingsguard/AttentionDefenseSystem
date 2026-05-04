from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from .styles import get_btn_style

class CurrentRequestTab(QWidget):
    action_taken = pyqtSignal(dict)

    def __init__(self, requester: str, incoming_message: str, drafted_response: str):
        super().__init__()
        self.drafted_response = drafted_response
        self.init_ui(requester, incoming_message)

    def init_ui(self, requester: str, incoming_message: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(20)

        # Header
        header = QLabel("Agent Drafted a Response")
        header.setStyleSheet("color: #FFFFFF; font-size: 24px; font-weight: bold; font-family: Inter, Arial;")
        layout.addWidget(header)

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
        
        layout.addWidget(context_frame)

        # Draft label
        draft_lbl = QLabel("Proposed Status Update (Feel free to edit):")
        draft_lbl.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: bold; font-family: Inter, Arial;")
        layout.addWidget(draft_lbl)

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
        layout.addWidget(self.textbox)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        btn_approve = QPushButton("Approve & Send")
        btn_approve.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_approve.setStyleSheet(get_btn_style("#2E7D32", "#1B5E20"))
        btn_approve.clicked.connect(self.on_approve)
        
        btn_edit = QPushButton("Send Edited")
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet(get_btn_style("#1565C0", "#0D47A1"))
        btn_edit.clicked.connect(self.on_edit)
        
        btn_reject = QPushButton("Reject")
        btn_reject.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reject.setStyleSheet(get_btn_style("#C62828", "#b71c1c"))
        btn_reject.clicked.connect(self.on_reject)

        btn_layout.addWidget(btn_approve)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_reject)
        
        layout.addLayout(btn_layout)

    def on_approve(self):
        self.action_taken.emit({"action": "approve", "content": self.textbox.toPlainText().strip()})

    def on_edit(self):
        self.action_taken.emit({"action": "edit", "content": self.textbox.toPlainText().strip()})

    def on_reject(self):
        self.action_taken.emit({"action": "reject", "content": None})
