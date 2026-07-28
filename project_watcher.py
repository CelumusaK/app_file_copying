import os
from PyQt6.QtCore import QFileSystemWatcher, QObject, pyqtSignal
from utils import match_ignore

class ProjectWatcher(QObject):
    file_changed = pyqtSignal(str)
    directory_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.on_file_changed)
        self.watcher.directoryChanged.connect(self.on_directory_changed)
        self.watched_files = set()

    def set_project_folder(self, folder):
        if self.watcher.directories():
            self.watcher.removePaths(self.watcher.directories())
        if self.watcher.files():
            self.watcher.removePaths(self.watcher.files())
        
        self.watched_files.clear()
        
        if os.path.exists(folder):
            self.watcher.addPath(folder)
            self._add_directory_watchers(folder)

    def watch_file(self, path):
        if path not in self.watched_files and os.path.exists(path):
            self.watcher.addPath(path)
            self.watched_files.add(path)

    def _add_directory_watchers(self, directory):
        try:
            items = os.listdir(directory)
            for item in items:
                full_path = os.path.join(directory, item)
                is_dir = os.path.isdir(full_path)
                
                if match_ignore(item, is_dir):
                    continue
                    
                if is_dir:
                    self.watcher.addPath(full_path)
                    self._add_directory_watchers(full_path)
        except (PermissionError, FileNotFoundError):
            pass

    def on_file_changed(self, path):
        self.file_changed.emit(path)

    def on_directory_changed(self, path):
        self.directory_changed.emit()