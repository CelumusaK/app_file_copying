import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QCursor
from PyQt6.QtCore import Qt
from utils import generate_tree_text

def get_relative_path(full_path, root_folder):
    try:
        return os.path.relpath(full_path, root_folder)
    except:
        return full_path

def read_file_content(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def copy_files_to_clipboard(parent_widget, file_paths, root_folder):
    if not file_paths:
        return

    QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
    try:
        output = []
        for file_path in sorted(list(file_paths)):
            content = read_file_content(file_path)
            relative_path = get_relative_path(file_path, root_folder)
            
            output.append(f"File: {relative_path}")
            output.append("=" * 80)
            output.append(content)
            output.append("\n")
        
        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join(output))
        
    finally:
        QApplication.restoreOverrideCursor()

    QMessageBox.information(
        parent_widget, 
        "Copied", 
        f"{len(file_paths)} file(s) gathered and copied to clipboard!"
    )

def copy_project_tree(parent_widget, root_folder):
    if root_folder and os.path.exists(root_folder):
        tree_text = generate_tree_text(root_folder)
        clipboard = QApplication.clipboard()
        clipboard.setText(tree_text)
        QMessageBox.information(parent_widget, "Copied", "Project tree copied to clipboard!")