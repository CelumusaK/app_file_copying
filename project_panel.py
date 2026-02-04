import os
from PyQt6.QtWidgets import (
    QWidget, QTreeWidget, QTreeWidgetItem, QTextEdit, QSplitter,
    QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QToolBar, QMessageBox, QLineEdit, QLabel, QMenu, QSizePolicy
)
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtCore import Qt, pyqtSignal

from tree_builder import build_tree
from utils import get_recursive_files, FILTER_SETTINGS
from file_ops import copy_files_to_clipboard, copy_project_tree, read_file_content
from project_watcher import ProjectWatcher
from ignore_manager import IgnoreManagerWindow 

class ProjectPanel(QWidget):
    close_requested = pyqtSignal(object)
    add_requested = pyqtSignal()

    def __init__(self, default_folder=None):
        super().__init__()
        self.root_folder = None
        self.current_preview_path = None
        
        self.setStyleSheet("""
            QSplitter::handle { background-color: #3d3d3d; width: 1px; }
            QToolBar { background-color: #323232; border-bottom: 1px solid #111; spacing: 5px; }
            QTreeWidget, QTextEdit { border: none; background-color: #2b2b2b; color: #e0e0e0; }
            QTreeWidget::item:hover { background-color: #3d4b5c; }
            QTreeWidget::item:selected { background-color: #2d5a88; color: white; }
            QPushButton { background-color: #444; border: 1px solid #555; padding: 2px 5px; font-size: 11px; color: #eee; }
            QPushButton:hover { background-color: #555; }
            QLineEdit { background: #1e1e1e; color: #ccc; border: 1px solid #444; height: 18px; padding: 0 5px; }
        """)

        self.watcher = ProjectWatcher()
        self.watcher.file_changed.connect(self.handle_file_change)
        self.watcher.directory_changed.connect(self.reload_tree)

        # 1. Create the widgets first so they exist for the toolbar to use
        self.create_widgets()
        # 2. Setup the UI layout
        self.setup_ui()

        if default_folder and os.path.isdir(default_folder):
            self.load_project(default_folder)

    def create_widgets(self):
        """Initialize all main components before layout"""
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True) 
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        self.viewer = QTextEdit()
        self.viewer.setReadOnly(True)
        self.viewer.setFont(QFont("Consolas", 10))
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Filter...")
        self.search_bar.setFixedWidth(100)
        
        self.token_label = QLabel("Ready")
        self.token_label.setStyleSheet("font-size: 10px; color: #888;")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- TOOLBAR ---
        toolbar = QToolBar()
        toolbar.setMovable(False)
        
        # Workspace Controls
        add_act = QAction("➕", self)
        add_act.setToolTip("Split/Add View")
        add_act.triggered.connect(lambda: self.add_requested.emit())
        toolbar.addAction(add_act)

        browse_act = QAction("📁", self)
        browse_act.triggered.connect(self.browse_folder)
        toolbar.addAction(browse_act)
        
        toolbar.addSeparator()

        # Connections to already created widgets
        self.search_bar.textChanged.connect(self.filter_tree)
        toolbar.addWidget(self.search_bar)

        expand_act = QAction("⬇", self)
        expand_act.triggered.connect(self.tree.expandAll)
        toolbar.addAction(expand_act)

        manage_ignore_act = QAction("🚫", self)
        manage_ignore_act.triggered.connect(self.open_ignore_manager)
        toolbar.addAction(manage_ignore_act)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        self.show_hidden_act = QAction("👁", self)
        self.show_hidden_act.setCheckable(True)
        self.show_hidden_act.toggled.connect(self.toggle_hidden_files)
        toolbar.addAction(self.show_hidden_act)

        close_act = QAction("❌", self)
        close_act.triggered.connect(lambda: self.close_requested.emit(self))
        toolbar.addAction(close_act)

        layout.addWidget(toolbar)

        # --- BODY (Splitter) ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.tree)
        splitter.addWidget(self.viewer)
        splitter.setSizes([200, 800])
        layout.addWidget(splitter)

        # --- FOOTER ---
        footer = QWidget()
        footer.setFixedHeight(22)
        footer.setStyleSheet("background-color: #222; border-top: 1px solid #111;")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(5, 0, 5, 0)
        
        f_layout.addWidget(self.token_label)
        f_layout.addStretch()
        
        btn_copy_tree = QPushButton("Tree")
        btn_copy_tree.clicked.connect(lambda: copy_project_tree(self, self.root_folder))
        f_layout.addWidget(btn_copy_tree)
        
        btn_copy_files = QPushButton("Content")
        btn_copy_files.clicked.connect(self.gather_and_copy_files)
        f_layout.addWidget(btn_copy_files)
        
        layout.addWidget(footer)

        # Connect Events
        self.tree.customContextMenuRequested.connect(self.open_context_menu)
        self.tree.itemClicked.connect(self.on_item_click)
        self.tree.itemSelectionChanged.connect(self.update_token_estimate)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Root", os.path.expanduser("~"))
        if folder: self.load_project(folder)

    def load_project(self, folder):
        self.root_folder = folder
        self.reload_tree()
        self.watcher.set_project_folder(folder)

    def reload_tree(self):
        if not self.root_folder: return
        self.tree.clear()
        root_item = QTreeWidgetItem(self.tree, [os.path.basename(self.root_folder)])
        root_item.setData(0, Qt.ItemDataRole.UserRole, self.root_folder)
        font = root_item.font(0)
        font.setBold(True)
        root_item.setFont(0, font)
        
        build_tree(root_item, self.root_folder)
        self.tree.expandToDepth(1)
        if self.search_bar.text(): self.filter_tree(self.search_bar.text())

    def open_context_menu(self, position):
        item = self.tree.itemAt(position)
        if not item: return
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path == self.root_folder: return

        menu = QMenu()
        hide_act = menu.addAction(f"Hide '{item.text(0)}'")
        action = menu.exec(self.tree.viewport().mapToGlobal(position))
        if action == hide_act:
            FILTER_SETTINGS["custom_ignored"].add(item.text(0))
            self.reload_tree()

    def open_ignore_manager(self):
        if not self.root_folder: return
        dialog = IgnoreManagerWindow(
            self, self.root_folder, 
            FILTER_SETTINGS["custom_ignored"],
            FILTER_SETTINGS["temp_visible"],
            FILTER_SETTINGS["temp_ignored"]
        )
        if dialog.exec():
            ignored, visible, temp_ignored = dialog.get_final_sets()
            FILTER_SETTINGS["custom_ignored"] = ignored
            FILTER_SETTINGS["temp_visible"] = visible
            FILTER_SETTINGS["temp_ignored"] = temp_ignored
            self.reload_tree()

    def toggle_hidden_files(self, checked):
        FILTER_SETTINGS["show_hidden"] = checked
        self.reload_tree()

    def filter_tree(self, text):
        search_text = text.lower()
        def search_items(item):
            child_match = False
            for i in range(item.childCount()):
                if search_items(item.child(i)): child_match = True
            is_match = search_text in item.text(0).lower()
            should_show = is_match or child_match
            item.setHidden(not should_show)
            if should_show and search_text: item.setExpanded(True)
            return should_show
        
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            search_items(root.child(i))

    def on_item_click(self, item, column):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if os.path.isfile(path):
            self.current_preview_path = path
            self.viewer.setPlainText(read_file_content(path))
            self.watcher.watch_file(path)
        else:
            self.viewer.clear()

    def update_token_estimate(self):
        selected_items = self.tree.selectedItems()
        total_bytes = 0
        file_count = 0
        for item in selected_items:
            path = item.data(0, Qt.ItemDataRole.UserRole)
            try:
                if os.path.isfile(path):
                    total_bytes += os.path.getsize(path)
                    file_count += 1
                elif os.path.isdir(path):
                    files = get_recursive_files(path)
                    for f in files:
                        total_bytes += os.path.getsize(f)
                        file_count += 1
            except: pass
        
        tokens = int(total_bytes / 4)
        token_str = f"{tokens/1000:.1f}k" if tokens > 1000 else str(tokens)
        self.token_label.setText(f"{file_count} selected (~{token_str} tokens)")

    def gather_and_copy_files(self):
        selected_items = self.tree.selectedItems()
        if not selected_items: return
        files_to_copy = set()
        for item in selected_items:
            path = item.data(0, Qt.ItemDataRole.UserRole)
            if os.path.isfile(path): files_to_copy.add(path)
            elif os.path.isdir(path): files_to_copy.update(get_recursive_files(path))
        if files_to_copy:
            copy_files_to_clipboard(self, files_to_copy, self.root_folder)

    def handle_file_change(self, path):
        if path == self.current_preview_path and os.path.exists(path):
            self.viewer.setPlainText(read_file_content(path))