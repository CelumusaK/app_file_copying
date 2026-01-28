import sys
import os
from PyQt6.QtWidgets import (
    QApplication,
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
)
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtCore import Qt, QFileSystemWatcher


# --- Comprehensive ignore patterns for Flutter projects ---
IGNORED = {
    # Version Control
    ".git", ".gitignore", ".gitattributes",
    
    # IDE/Editor
    ".idea", ".vscode", ".editorconfig", ".DS_Store", ".venv",
    
    # Flutter/Dart Build
    ".dart_tool", ".flutter-plugins", ".flutter-plugins-dependencies",
    ".metadata", ".packages", "build", ".gradle", ".kotlin",
    "*.iml", "*.g.dart", "*.freezed.dart", "*.mocks.dart",
    
    # Platform-specific build artifacts
    "android/.gradle", "android/gradle", "android/local.properties",
    "android/.kotlin", "android/gradlew", "android/gradlew.bat",
    "ios/Flutter/ephemeral", "ios/Pods", "ios/Podfile.lock",
    "macos/Flutter/ephemeral", "macos/Pods",
    "linux/flutter/ephemeral", "windows/flutter/ephemeral",
    
    # Generated files
    "generated_plugin_registrant.dart", "generated_plugins.cmake",
    "GeneratedPluginRegistrant.java", "GeneratedPluginRegistrant.swift",
    "GeneratedPluginRegistrant.h", "GeneratedPluginRegistrant.m",
    
    # Node/JS (if using web)
    "node_modules", ".yarn", ".turbo", "dist",
    "*.lock", "yarn.lock", "package-lock.json",
    
    # Logs and temp
    "*.log", "*.pyc", "__pycache__", ".cache", ".cookie",
    ".expo", "*.swp", "*.bak",
    
    # Environment
    ".env", ".env.local",
    
    # Binary/Media that don't need review
    "*.png", "*.jpg", "*.jpeg", "*.ico", "*.jar",
    "*.exe", "*.dll", "*.so", "*.dylib",
    
    # Specific Flutter files that are auto-generated
    "flutter_export_environment.sh", "AppFrameworkInfo.plist",
    "ephemeral", ".plugin_symlinks",
    
    # Gradle wrapper
    "gradle-wrapper.jar", "gradle-wrapper.properties",
    
    # Xcode
    "*.xcworkspace", "*.xcodeproj", "xcshareddata",
    "IDEWorkspaceChecks.plist", "WorkspaceSettings.xcsettings",
    
    # Test/Example directories in plugins
    "test_driver", "integration_test",
    
    # Native build files
    "*.rc", "*.manifest", "runner.exe.manifest",
    
    # CMake
    "CMakeLists.txt", "*.cmake",

    #files
    "migrate.py", "history.json", "update_id.py",
}

# Directories to completely skip (never traverse into)
SKIP_DIRS = {
    ".dart_tool",
    ".gradle",
    ".idea",
    "build",
    "ephemeral",
    ".plugin_symlinks",
    "Pods",
    "node_modules",
    "__pycache__",
    ".git",
    "linux/flutter/ephemeral",
    "windows/flutter/ephemeral",
    "macos/Flutter/ephemeral",
    "ios/Flutter/ephemeral",
}

def match_ignore(name, is_dir=False):
    """Check if a file/folder should be ignored"""
    # Check if directory should be completely skipped
    if is_dir and name in SKIP_DIRS:
        return True
    
    for pattern in IGNORED:
        # Exact match
        if name == pattern:
            return True
        # Wildcard extension match
        if pattern.startswith("*") and name.endswith(pattern[1:]):
            return True
    return False

def build_tree(parent, path):
    """Recursively build QTreeWidgetItem tree with improved filtering"""
    try:
        items = sorted(os.listdir(path))
    except PermissionError:
        return
    
    for item in items:
        full_path = os.path.join(path, item)
        is_dir = os.path.isdir(full_path)
        
        # Skip ignored items
        if match_ignore(item, is_dir):
            continue
            
        node = QTreeWidgetItem(parent, [item])
        node.setData(0, Qt.ItemDataRole.UserRole, full_path)
        
        if is_dir:
            build_tree(node, full_path)

def generate_tree_text(root):
    """Generate a clean text representation with filtering"""
    tree = []
    
    def walk(dir_path, prefix=""):
        try:
            items = sorted(os.listdir(dir_path))
        except PermissionError:
            return
        
        # Filter out ignored items
        filtered_items = []
        for item in items:
            full_path = os.path.join(dir_path, item)
            is_dir = os.path.isdir(full_path)
            if not match_ignore(item, is_dir):
                filtered_items.append(item)
        
        for i, item in enumerate(filtered_items):
            full_path = os.path.join(dir_path, item)
            connector = "├─ " if i < len(filtered_items) - 1 else "└─ "
            tree.append(f"{prefix}{connector}{item}")
            
            if os.path.isdir(full_path):
                extension = "│  " if i < len(filtered_items) - 1 else "   "
                walk(full_path, prefix + extension)
    
    tree.append(os.path.basename(root) + "/")
    walk(root)
    return "\n".join(tree)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    default_path = "/home/lazydev/flutter/twb_roleplay"
    window = MainWindow(default_path)
    window.show()
    sys.exit(app.exec())