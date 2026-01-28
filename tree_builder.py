import os
from PyQt6.QtWidgets import QTreeWidgetItem
from PyQt6.QtCore import Qt
from utils import match_ignore

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