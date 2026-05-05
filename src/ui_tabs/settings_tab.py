from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QComboBox, QLineEdit, QStackedWidget, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from db import get_data_connectors, upsert_data_connector, delete_data_connector, clear_connector_data
from .styles import get_btn_style, get_combo_style
import os
from ingest import sync_connectors

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Sidebar
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(200)
        sidebar_frame.setStyleSheet("background-color: #2B2B2B; border-radius: 8px;")
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        btn_email = QPushButton("Email Connectors")
        btn_git = QPushButton("Git Connectors")
        btn_add = QPushButton("+ Add New Connector")
        
        for btn in [btn_email, btn_git, btn_add]:
            btn.setStyleSheet(get_btn_style("#3B3B3B", "#555555"))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            sidebar_layout.addWidget(btn)
            
        layout.addWidget(sidebar_frame)
        
        # Content Area
        self.settings_stack = QStackedWidget()
        layout.addWidget(self.settings_stack)
        
        # Pages
        self.page_email = QWidget()
        self.init_connector_list_page(self.page_email, "email_imap", "Email Connectors")
        self.settings_stack.addWidget(self.page_email)
        
        self.page_git = QWidget()
        self.init_connector_list_page(self.page_git, "local_git", "Git Connectors")
        self.settings_stack.addWidget(self.page_git)
        
        self.page_add = QWidget()
        self.init_add_connector_page(self.page_add)
        self.settings_stack.addWidget(self.page_add)
        
        # Wiring
        btn_email.clicked.connect(lambda: self.switch_settings_page(0))
        btn_git.clicked.connect(lambda: self.switch_settings_page(1))
        btn_add.clicked.connect(lambda: self.switch_settings_page(2))
        
    def switch_settings_page(self, index):
        self.settings_stack.setCurrentIndex(index)
        if index == 0:
            self.refresh_connector_list(self.page_email, "email_imap")
        elif index == 1:
            self.refresh_connector_list(self.page_git, "local_git")

    def init_connector_list_page(self, parent_widget, c_type, title):
        layout = QVBoxLayout(parent_widget)
        
        header = QLabel(title)
        header.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: bold; font-family: Inter, Arial;")
        layout.addWidget(header)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        content.layout = QVBoxLayout(content)
        content.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        parent_widget.list_layout = content.layout
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.refresh_connector_list(parent_widget, c_type)
        
    def refresh_connector_list(self, parent_widget, c_type):
        layout = parent_widget.list_layout
        while layout.count():
            child = layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            
        connectors = [c for c in get_data_connectors() if c["type"] == c_type]
        if not connectors:
            lbl = QLabel("No connectors configured.")
            lbl.setStyleSheet("color: #888888; font-size: 15px; font-style: italic;")
            layout.addWidget(lbl)
            return
            
        for c in connectors:
            frame = QFrame()
            frame.setStyleSheet("QFrame { background-color: #2B2B2B; border-radius: 8px; border: 1px solid #3B3B3B; }")
            flayout = QHBoxLayout(frame)
            
            info_layout = QVBoxLayout()
            id_lbl = QLabel(f"<b>ID:</b> {c['id']}")
            id_lbl.setStyleSheet("color: #E0E0E0; font-size: 14px;")
            info_layout.addWidget(id_lbl)
            
            if c_type == "email_imap":
                det = QLabel(f"Host: {c['config'].get('host')} | User: {c['config'].get('user')}")
            else:
                det = QLabel(f"Repo: {c['config'].get('repo_path')}")
            det.setStyleSheet("color: #AAAAAA; font-size: 12px;")
            info_layout.addWidget(det)
            
            flayout.addLayout(info_layout)
            
            btn_del = QPushButton("Delete")
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setStyleSheet(get_btn_style("#C62828", "#b71c1c"))
            btn_del.clicked.connect(lambda checked, cid=c['id'], pt=parent_widget, ct=c_type: self.delete_connector(cid, pt, ct))
            flayout.addWidget(btn_del)
            
            btn_clear = QPushButton("Clear & Reload")
            btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_clear.setStyleSheet(get_btn_style("#F57C00", "#E65100"))
            btn_clear.clicked.connect(lambda checked, cid=c['id'], pt=parent_widget, ct=c_type: self.clear_and_reload_connector(cid, pt, ct))
            flayout.addWidget(btn_clear)
            
            layout.addWidget(frame)

    def delete_connector(self, cid, parent_widget, c_type):
        if delete_data_connector(cid):
            self.refresh_connector_list(parent_widget, c_type)

    def clear_and_reload_connector(self, cid, parent_widget, c_type):
        reply = QMessageBox.question(self, 'Confirm Clear & Reload',
                                     f'Are you sure you want to clear and reload all data for connector {cid}?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if clear_connector_data(cid):
                # Trigger sync specifically for this connector
                sync_connectors(target_connector_id=cid)
                QMessageBox.information(self, 'Success', f'Connector {cid} has been successfully cleared and reloaded.')
                self.refresh_connector_list(parent_widget, c_type)
            else:
                QMessageBox.warning(self, 'Error', f'Failed to clear data for {cid}.')

    def init_add_connector_page(self, parent_widget):
        layout = QVBoxLayout(parent_widget)
        
        header = QLabel("Add New Connector")
        header.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: bold; font-family: Inter, Arial;")
        layout.addWidget(header)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Email (IMAP)", "Local Git"])
        self.type_combo.setStyleSheet(get_combo_style())
        self.type_combo.currentTextChanged.connect(self.on_add_type_changed)
        layout.addWidget(self.type_combo)
        
        self.form_frame = QFrame()
        self.form_layout = QFormLayout(self.form_frame)
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        input_style = "QLineEdit { background-color: #2B2B2B; color: #FFFFFF; border: 1px solid #3B3B3B; border-radius: 5px; padding: 8px; } QLineEdit:focus { border: 1px solid #5C6BC0; }"
        
        self.inp_email_host = QLineEdit(); self.inp_email_host.setStyleSheet(input_style)
        self.inp_email_user = QLineEdit(); self.inp_email_user.setStyleSheet(input_style)
        self.inp_email_pass = QLineEdit(); self.inp_email_pass.setStyleSheet(input_style); self.inp_email_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_email_folder = QLineEdit("INBOX"); self.inp_email_folder.setStyleSheet(input_style)
        
        self.inp_git_repo = QLineEdit(); self.inp_git_repo.setStyleSheet(input_style)
        
        layout.addWidget(self.form_frame)
        
        btn_save = QPushButton("Save Connector")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(get_btn_style("#2E7D32", "#1B5E20"))
        btn_save.clicked.connect(self.save_new_connector)
        layout.addWidget(btn_save)
        layout.addStretch()
        
        self.on_add_type_changed()
        
    def on_add_type_changed(self):
        while self.form_layout.rowCount() > 0:
            self.form_layout.removeRow(0)
            
        c_type = self.type_combo.currentText()
        label_style = "color: #E0E0E0; font-weight: bold; font-family: Inter, Arial;"
        
        def create_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(label_style)
            return lbl
            
        if c_type == "Email (IMAP)":
            self.form_layout.addRow(create_label("IMAP Server:"), self.inp_email_host)
            self.form_layout.addRow(create_label("Username:"), self.inp_email_user)
            self.form_layout.addRow(create_label("Password:"), self.inp_email_pass)
            self.form_layout.addRow(create_label("Folder:"), self.inp_email_folder)
        else:
            self.form_layout.addRow(create_label("Repository Path:"), self.inp_git_repo)

    def save_new_connector(self):
        c_type = self.type_combo.currentText()
        if c_type == "Email (IMAP)":
            host = self.inp_email_host.text().strip()
            user = self.inp_email_user.text().strip()
            pwd = self.inp_email_pass.text().strip()
            folder = self.inp_email_folder.text().strip()
            
            if not host or not user or not pwd:
                return
                
            cid = f"email_{user}"
            config = {"host": host, "user": user, "password": pwd, "folder": folder}
            upsert_data_connector(cid, "email_imap", config)
            self.switch_settings_page(0)
            
        elif c_type == "Local Git":
            repo = self.inp_git_repo.text().strip()
            if not repo: return
            
            abs_path = os.path.abspath(repo)
            cid = f"git_{abs_path}"
            config = {"repo_path": repo}
            upsert_data_connector(cid, "local_git", config)
            self.switch_settings_page(1)
