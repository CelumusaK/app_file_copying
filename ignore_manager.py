import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
    QLineEdit, QPushButton, QLabel, QComboBox
)
from utils import FILTER_SETTINGS, save_settings
from constants import IGNORED, SKIP_DIRS

class AdvancedIgnoreManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Visibility Rules")
        self.resize(500, 500)
        self.setup_ui()
        self.load_rules()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        info = QLabel("Hide new files based on custom string matching rules.")
        info.setStyleSheet("color: #aaa; font-style: italic;")
        layout.addWidget(info)

        # Input Area
        add_layout = QHBoxLayout()
        self.rule_type = QComboBox()
        self.rule_type.addItems(["Exact Match", "Starts With", "Ends With", "Contains"])
        
        self.rule_input = QLineEdit()
        self.rule_input.setPlaceholderText("Enter pattern (e.g. _test.py)")
        
        btn_add = QPushButton("Add Rule")
        btn_add.clicked.connect(self.add_rule)
        
        add_layout.addWidget(self.rule_type)
        add_layout.addWidget(self.rule_input)
        add_layout.addWidget(btn_add)
        layout.addLayout(add_layout)

        # Rule List
        layout.addWidget(QLabel("Active Hidden Rules:"))
        self.rules_list = QListWidget()
        layout.addWidget(self.rules_list)
        
        btn_remove = QPushButton("🗑️ Remove Selected Rule")
        btn_remove.clicked.connect(self.remove_rule)
        layout.addWidget(btn_remove)
        
        # Exception List (temp_visible)
        layout.addWidget(QLabel("Always Visible (Exceptions):"))
        self.exceptions_list = QListWidget()
        layout.addWidget(self.exceptions_list)
        
        btn_remove_ex = QPushButton("🗑️ Remove Selected Exception")
        btn_remove_ex.clicked.connect(self.remove_exception)
        layout.addWidget(btn_remove_ex)

        # Save and Close
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_close = QPushButton("💾 Save & Apply")
        btn_close.clicked.connect(self.save_and_close)
        btn_close.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; padding: 8px 20px;")
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        self.setStyleSheet("""
            QDialog { background-color: #2b2b2b; color: #e0e0e0; }
            QListWidget { background-color: #3c3f41; color: #e0e0e0; border: 1px solid #555; }
            QLineEdit, QComboBox { background-color: #3c3f41; color: #e0e0e0; padding: 5px; border: 1px solid #555; }
            QPushButton { background-color: #444; color: white; border: 1px solid #555; padding: 5px; }
            QPushButton:hover { background-color: #555; }
        """)

    def load_rules(self):
        for r in FILTER_SETTINGS["rules_exact"]: self.rules_list.addItem(f"[Exact Match] {r}")
        for r in FILTER_SETTINGS["rules_startswith"]: self.rules_list.addItem(f"[Starts With] {r}")
        for r in FILTER_SETTINGS["rules_endswith"]: self.rules_list.addItem(f"[Ends With] {r}")
        for r in FILTER_SETTINGS["rules_contains"]: self.rules_list.addItem(f"[Contains] {r}")
        
        for ex in FILTER_SETTINGS["temp_visible"]:
            self.exceptions_list.addItem(ex)

    def add_rule(self):
        val = self.rule_input.text().strip()
        if not val: return
        rtype = self.rule_type.currentText()
        self.rules_list.addItem(f"[{rtype}] {val}")
        self.rule_input.clear()

    def remove_rule(self):
        item = self.rules_list.currentItem()
        if item: self.rules_list.takeItem(self.rules_list.row(item))

    def remove_exception(self):
        item = self.exceptions_list.currentItem()
        if item: self.exceptions_list.takeItem(self.exceptions_list.row(item))

    def save_and_close(self):
        FILTER_SETTINGS["rules_exact"] = []
        FILTER_SETTINGS["rules_startswith"] = []
        FILTER_SETTINGS["rules_endswith"] = []
        FILTER_SETTINGS["rules_contains"] = []
        
        for i in range(self.rules_list.count()):
            text = self.rules_list.item(i).text()
            val = text.split("] ", 1)[1]
            if "[Exact Match]" in text: FILTER_SETTINGS["rules_exact"].append(val)
            elif "[Starts With]" in text: FILTER_SETTINGS["rules_startswith"].append(val)
            elif "[Ends With]" in text: FILTER_SETTINGS["rules_endswith"].append(val)
            elif "[Contains]" in text: FILTER_SETTINGS["rules_contains"].append(val)
        
        FILTER_SETTINGS["temp_visible"] = []
        for i in range(self.exceptions_list.count()):
            FILTER_SETTINGS["temp_visible"].append(self.exceptions_list.item(i).text())
            
        save_settings()
        self.accept()


class DefaultHiddenDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Default Hidden Files")
        self.resize(400, 600)
        layout = QVBoxLayout(self)
        
        lbl = QLabel("These items are hidden by default from constants.py:")
        lbl.setStyleSheet("color: #ccc; font-weight: bold;")
        layout.addWidget(lbl)
        
        list_widget = QListWidget()
        layout.addWidget(list_widget)
        
        combined = sorted(list(IGNORED.union(SKIP_DIRS)))
        list_widget.addItems(combined)
        
        btn = QPushButton("Close")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
        
        self.setStyleSheet("""
            QDialog { background-color: #2b2b2b; color: #e0e0e0; }
            QListWidget { background-color: #3c3f41; color: #e0e0e0; border: 1px solid #555; }
            QPushButton { background-color: #444; color: white; padding: 5px; }
        """)