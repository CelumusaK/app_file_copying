import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, 
    QLineEdit, QPushButton, QLabel, QComboBox, QStyle, QApplication,
    QWidget
)
from PyQt6.QtCore import Qt
from constants import SKIP_DIRS, IGNORED

class IgnoreManagerWindow(QDialog):
    def __init__(self, parent, root_folder, current_ignored_set, temp_visible, temp_ignored):
        super().__init__(parent)
        self.setWindowTitle("Manage Visibility (Mini Explorer)")
        self.resize(600, 700)
        self.root_folder = root_folder
        
        self.working_ignored = set(current_ignored_set)
        self.working_temp_visible = set(temp_visible)
        self.working_temp_ignored = set(temp_ignored)
        
        self.setup_ui()
        self.load_tree()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        info = QLabel("Check items to HIDE them from the main explorer.\nUncheck to make them VISIBLE.")
        info.setStyleSheet("color: #aaa; font-style: italic;")
        layout.addWidget(info)

        controls_layout = QHBoxLayout()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search files...")
        self.search_bar.textChanged.connect(self.filter_tree)
        
        self.view_combo = QComboBox()
        self.view_combo.addItems(["View All Files", "Show Only Hidden", "Show Only Visible"])
        self.view_combo.currentIndexChanged.connect(self.filter_tree)
        
        controls_layout.addWidget(self.search_bar, 3)
        controls_layout.addWidget(self.view_combo, 1)
        layout.addLayout(controls_layout)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Project Files")
        self.tree.setFont(QApplication.font())
        self.tree.itemChanged.connect(self.on_item_changed)
        layout.addWidget(self.tree)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setStyleSheet("background-color: #555; color: white; padding: 8px;")
        
        btn_save = QPushButton("💾 Apply Changes")
        btn_save.clicked.connect(self.accept)
        btn_save.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; padding: 8px 20px;")
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)
        
        self.setStyleSheet("""
            QDialog { background-color: #2b2b2b; color: #e0e0e0; }
            QTreeWidget { background-color: #3c3f41; color: #e0e0e0; border: 1px solid #555; }
            QTreeWidget::item:hover { background-color: #4b6eaf; }
            QLineEdit, QComboBox { background-color: #3c3f41; color: #e0e0e0; padding: 5px; border: 1px solid #555; }
        """)

    def get_icon(self, is_dir):
        style = QApplication.style()
        if is_dir:
            return style.standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        return style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)

    def load_tree(self):
        self.tree.blockSignals(True)
        self.tree.clear()
        
        root_item = QTreeWidgetItem(self.tree, [os.path.basename(self.root_folder)])
        root_item.setData(0, Qt.ItemDataRole.UserRole, self.root_folder)
        root_item.setIcon(0, self.get_icon(True))
        root_item.setExpanded(True)
        
        self.recursive_build(root_item, self.root_folder)
        
        self.tree.blockSignals(False)

    def recursive_build(self, parent_node, current_path):
        try:
            items = sorted(os.listdir(current_path))
        except PermissionError:
            return

        dirs = []
        files = []
        
        for item in items:
            full_path = os.path.join(current_path, item)
            is_dir = os.path.isdir(full_path)
            
            if is_dir and item in SKIP_DIRS:
                continue
                
            if is_dir:
                dirs.append((item, full_path))
            else:
                files.append((item, full_path))

        for name, path in dirs:
            node = QTreeWidgetItem(parent_node, [name])
            node.setData(0, Qt.ItemDataRole.UserRole, path)
            node.setIcon(0, self.get_icon(True))
            self.set_node_state(node, name)
            self.recursive_build(node, path)

        for name, path in files:
            node = QTreeWidgetItem(parent_node, [name])
            node.setData(0, Qt.ItemDataRole.UserRole, path)
            node.setIcon(0, self.get_icon(False))
            self.set_node_state(node, name)

    def is_in_constants(self, name):
        if name in IGNORED:
            return True
        for pattern in IGNORED:
            if pattern.startswith("*") and name.endswith(pattern[1:]):
                return True
        return False

    def set_node_state(self, node, name):
        node.setFlags(node.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        
        in_constants = self.is_in_constants(name)
        
        if name in self.working_temp_visible:
            node.setCheckState(0, Qt.CheckState.Unchecked)
            node.setForeground(0, Qt.GlobalColor.green)
        elif name in self.working_temp_ignored:
            node.setCheckState(0, Qt.CheckState.Checked)
            node.setForeground(0, Qt.GlobalColor.yellow)
        elif name in self.working_ignored:
            node.setCheckState(0, Qt.CheckState.Checked)
            node.setForeground(0, Qt.GlobalColor.red)
        elif in_constants:
            node.setCheckState(0, Qt.CheckState.Checked)
            node.setForeground(0, Qt.GlobalColor.darkRed)
        else:
            node.setCheckState(0, Qt.CheckState.Unchecked)
            node.setForeground(0, Qt.GlobalColor.lightGray)

    def on_item_changed(self, item, column):
        name = item.text(0)
        state = item.checkState(0)
        in_constants = self.is_in_constants(name)
        
        if state == Qt.CheckState.Checked:
            self.working_temp_visible.discard(name)
            
            if in_constants:
                item.setForeground(0, Qt.GlobalColor.darkRed)
            else:
                self.working_ignored.add(name)
                self.working_temp_ignored.discard(name)
                item.setForeground(0, Qt.GlobalColor.red)
        else:
            self.working_ignored.discard(name)
            self.working_temp_ignored.discard(name)
            
            if in_constants:
                self.working_temp_visible.add(name)
                item.setForeground(0, Qt.GlobalColor.green)
            else:
                self.working_temp_visible.discard(name)
                item.setForeground(0, Qt.GlobalColor.lightGray)
            
        if self.view_combo.currentIndex() != 0: 
            self.filter_tree()

    def filter_tree(self):
        search_text = self.search_bar.text().lower()
        view_mode = self.view_combo.currentIndex()

        def process_node(node):
            child_visible = False
            for i in range(node.childCount()):
                if process_node(node.child(i)):
                    child_visible = True
            
            name = node.text(0)
            in_constants = self.is_in_constants(name)
            
            is_ignored = False
            if name in self.working_temp_visible:
                is_ignored = False
            elif name in self.working_temp_ignored or name in self.working_ignored or in_constants:
                is_ignored = True
            
            mode_match = True
            if view_mode == 1 and not is_ignored:
                mode_match = False
            elif view_mode == 2 and is_ignored:
                mode_match = False
                
            search_match = True
            if search_text:
                search_match = search_text in name.lower()
            
            should_show = (mode_match and search_match) or child_visible
            
            node.setHidden(not should_show)
            if should_show and (search_text or view_mode != 0):
                node.setExpanded(True)
                
            return should_show

        root = self.tree.topLevelItem(0)
        if root:
            process_node(root)

    def get_final_sets(self):
        return self.working_ignored, self.working_temp_visible, self.working_temp_ignored