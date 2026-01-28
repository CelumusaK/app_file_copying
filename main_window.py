import os
from PyQt6.QtWidgets import (
    QMainWindow,
    QTreeWidget,
    QTreeWidgetItem,
    QTextEdit,
    QSplitter,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QFileDialog,
    QToolBar,
    QMessageBox,
    QApplication
)
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtCore import Qt, QFileSystemWatcher

from utils import match_ignore, generate_tree_text
from tree_builder import build_tree

class MainWindow(QMainWindow):
    def __init__(self, default_folder):
        super().__init__()
        self.setWindowTitle("Flutter Project Explorer")
        self.resize(1200, 800)
        self.selected_files = []
        
        # Initialize file system watcher
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.fileChanged.connect(self.on_file_changed)
        self.file_watcher.directoryChanged.connect(self.on_directory_changed)

        # Toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        browse_action = QAction("Browse Folder", self)
        browse_action.triggered.connect(self.browse_folder)
        toolbar.addAction(browse_action)
        
        toolbar.addSeparator()
        
        expand_action = QAction("Expand All", self)
        expand_action.triggered.connect(self.expand_all)
        toolbar.addAction(expand_action)
        
        collapse_action = QAction("Collapse All", self)
        collapse_action.triggered.connect(self.collapse_all)
        toolbar.addAction(collapse_action)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Tree Widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Project Structure (Filtered)")
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        tree_font = QFont("Monospace", 10)
        self.tree.setFont(tree_font)
        self.tree.itemClicked.connect(self.on_item_click)
        splitter.addWidget(self.tree)

        # File viewer
        self.viewer = QTextEdit()
        self.viewer.setReadOnly(True)
        viewer_font = QFont("Monospace", 10)
        self.viewer.setFont(viewer_font)
        splitter.addWidget(self.viewer)

        splitter.setSizes([400, 800])

        # Button layout
        button_layout = QHBoxLayout()
        
        copy_tree_btn = QPushButton("Copy Project Tree")
        copy_tree_btn.clicked.connect(self.copy_tree)
        button_layout.addWidget(copy_tree_btn)

        copy_selected_btn = QPushButton("Copy Selected Files")
        copy_selected_btn.clicked.connect(self.copy_selected_files)
        button_layout.addWidget(copy_selected_btn)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Load default project folder
        if os.path.isdir(default_folder):
            self.load_project(default_folder)
        else:
            self.browse_folder()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Root", os.path.expanduser("~"))
        if folder:
            self.load_project(folder)

    def load_project(self, folder):
        self.tree.clear()
        self.root_folder = folder
        
        if self.file_watcher.directories():
            self.file_watcher.removePaths(self.file_watcher.directories())
        if self.file_watcher.files():
            self.file_watcher.removePaths(self.file_watcher.files())
            
        self.file_watcher.addPath(folder)
        self.add_directory_watchers(folder)
        
        root_item = QTreeWidgetItem(self.tree, [os.path.basename(folder)])
        root_item.setData(0, Qt.ItemDataRole.UserRole, folder)
        build_tree(root_item, folder)
        self.tree.expandToDepth(1)

    def add_directory_watchers(self, directory):
        """Recursively add directory watchers (skip ignored dirs)"""
        try:
            items = os.listdir(directory)
            for item in items:
                full_path = os.path.join(directory, item)
                is_dir = os.path.isdir(full_path)
                
                if match_ignore(item, is_dir):
                    continue
                    
                if is_dir:
                    self.file_watcher.addPath(full_path)
                    self.add_directory_watchers(full_path)
        except (PermissionError, FileNotFoundError):
            pass

    def on_item_click(self, item, column):
        selected_items = self.tree.selectedItems()
        self.selected_files = []
        
        for item in selected_items:
            path = item.data(0, Qt.ItemDataRole.UserRole)
            if os.path.isfile(path):
                self.selected_files.append(path)
        
        # Show preview of first selected file
        if self.selected_files:
            self.load_file_content(self.selected_files[0])
        else:
            self.viewer.clear()

    def load_file_content(self, path):
        """Load file content into viewer"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.viewer.setPlainText(content)
        except Exception as e:
            self.viewer.setPlainText(f"Cannot open file: {e}")

    def get_relative_path(self, full_path):
        """Get path relative to root folder"""
        try:
            return os.path.relpath(full_path, self.root_folder)
        except:
            return full_path

    def copy_selected_files(self):
        """Copy all selected files with relative paths"""
        if not self.selected_files:
            QMessageBox.warning(self, "No Files Selected", "Please select one or more files!")
            return
        
        output = []
        
        for file_path in self.selected_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                relative_path = self.get_relative_path(file_path)
                output.append(f"File: {relative_path}")
                output.append("=" * 80)
                output.append(content)
                output.append("\n")
                
            except Exception as e:
                output.append(f"File: {self.get_relative_path(file_path)}")
                output.append("=" * 80)
                output.append(f"Error reading file: {e}")
                output.append("\n")
        
        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join(output))
        QMessageBox.information(self, "Copied", f"{len(self.selected_files)} file(s) copied to clipboard!")

    def on_file_changed(self, path):
        """Handle file change event"""
        if path in self.selected_files:
            if os.path.exists(path):
                self.load_file_content(path)
                if path not in self.file_watcher.files():
                    self.file_watcher.addPath(path)

    def on_directory_changed(self, path):
        """Handle directory change event"""
        if hasattr(self, "root_folder"):
            self.load_project(self.root_folder)

    def copy_tree(self):
        if hasattr(self, "root_folder"):
            tree_text = generate_tree_text(self.root_folder)
            clipboard = QApplication.clipboard()
            clipboard.setText(tree_text)
            QMessageBox.information(self, "Copied", "Project tree copied to clipboard!")

    def expand_all(self):
        """Expand all items in the tree"""
        self.tree.expandAll()

    def collapse_all(self):
        """Collapse all items in the tree"""
        self.tree.collapseAll()