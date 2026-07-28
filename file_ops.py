import os
import re
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

def create_project_from_tree(base_path, tree_text):
    """Parses an ASCII tree and creates the corresponding files and folders."""
    stack = [(-1, base_path)]
    
    # Strip markdown codeblocks if accidentally copied from LLM
    tree_text = re.sub(r'```[a-zA-Z]*\n', '', tree_text)
    tree_text = tree_text.replace('```', '')

    for line in tree_text.splitlines():
        if not line.strip():
            continue
            
        # Find the actual filename starting index (ignoring visual tree characters and spaces)
        match = re.search(r'[^\s│├└─]', line)
        if not match:
            continue
            
        indent = match.start()
        name = line[indent:].strip()
        
        is_dir = name.endswith('/')
        name = name.rstrip('/')
        
        if not name:
            continue
        
        # Pop stack to find the correct parent directory based on indentation
        while stack and stack[-1][0] >= indent:
            stack.pop()
            
        parent_path = stack[-1][1]
        
        # If the parent was previously created as a file (e.g., missing trailing slash heuristic),
        # convert it into a directory now that we know it has children!
        if os.path.isfile(parent_path):
            os.remove(parent_path)
            os.makedirs(parent_path, exist_ok=True)
            
        full_path = os.path.join(parent_path, name)
        
        if is_dir:
            os.makedirs(full_path, exist_ok=True)
        else:
            # Ensure the parent exists, then create the empty file
            os.makedirs(parent_path, exist_ok=True)
            if not os.path.exists(full_path):
                with open(full_path, 'a', encoding='utf-8') as f:
                    pass
                    
        stack.append((indent, full_path))