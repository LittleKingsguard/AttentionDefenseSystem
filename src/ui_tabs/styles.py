def get_btn_style(bg_color: str, hover_color: str) -> str:
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

def get_combo_style() -> str:
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
