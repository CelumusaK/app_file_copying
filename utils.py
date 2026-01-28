import os
from constants import IGNORED, SKIP_DIRS

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