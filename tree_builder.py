import os
from PyQt6.QtWidgets import QTreeWidgetItem, QApplication, QStyle
from PyQt6.QtCore import Qt
from utils import match_ignore

def get_icon(is_dir):
    """Get standard system icons for files/folders"""
    style = QApplication.style()
    if is_dir:
        return style.standardIcon(QStyle.StandardPixmap.SP_DirIcon)
    else:
        return style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)

def build_tree(parent, path):
    try:
        items = sorted(os.listdir(path))
    except PermissionError:
        return
    
    dirs = []
    files = []

    for item in items:
        full_path = os.path.join(path, item)
        is_dir = os.path.isdir(full_path)
        
        if match_ignore(item, is_dir):
            continue
            
        if is_dir:
            dirs.append((item, full_path))
        else:
            files.append((item, full_path))
            
    for name, full_path in dirs:
        node = QTreeWidgetItem(parent, [name])
        node.setData(0, Qt.ItemDataRole.UserRole, full_path)
        node.setIcon(0, get_icon(True))
        font = node.font(0)
        font.setBold(True)
        node.setFont(0, font)
        
        build_tree(node, full_path)

    for name, full_path in files:
        node = QTreeWidgetItem(parent, [name])
        node.setData(0, Qt.ItemDataRole.UserRole, full_path)
        node.setIcon(0, get_icon(False))