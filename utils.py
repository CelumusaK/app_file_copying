import os
from constants import IGNORED, SKIP_DIRS

FILTER_SETTINGS = {
    "show_hidden": False,
    "custom_ignored": set(),
    "temp_visible": set(),
    "temp_ignored": set(),
}

def match_ignore(name, is_dir=False):
    if name in FILTER_SETTINGS["temp_visible"]:
        return False
    
    if name in FILTER_SETTINGS["temp_ignored"]:
        return True
    
    if name in FILTER_SETTINGS["custom_ignored"]:
        return True

    if name.startswith("."):
        if FILTER_SETTINGS["show_hidden"]:
            if name in {".git", ".idea", ".vscode"}:
                return True
            return False
        else:
            return True

    if is_dir and name in SKIP_DIRS:
        return True
    
    for pattern in IGNORED:
        if name == pattern:
            return True
        if pattern.startswith("*") and name.endswith(pattern[1:]):
            return True
            
    return False

def get_recursive_files(directory):
    file_paths = []
    try:
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not match_ignore(d, is_dir=True)]
            
            for file in files:
                if not match_ignore(file, is_dir=False):
                    file_paths.append(os.path.join(root, file))
    except PermissionError:
        pass
    return file_paths

def generate_tree_text(root):
    tree = []
    
    def walk(dir_path, prefix=""):
        try:
            items = sorted(os.listdir(dir_path))
        except PermissionError:
            return
        
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