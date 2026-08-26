import os
import json
from constants import IGNORED, SKIP_DIRS

SETTINGS_FILE = "vibe_settings.json"

FILTER_SETTINGS = {
    "show_hidden": False,
    "rules_exact": [],
    "rules_startswith": [],
    "rules_endswith": [],
    "rules_contains": [],
    "temp_visible": [], # Exact names to ALWAYS show (Exceptions)
}

def load_settings():
    """Load user settings from a local JSON db file."""
    global FILTER_SETTINGS
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                saved = json.load(f)
                for key in FILTER_SETTINGS:
                    if key in saved:
                        FILTER_SETTINGS[key] = saved[key]
        except Exception as e:
            print(f"Error loading config: {e}")

def save_settings():
    """Save user settings to a local JSON db file."""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(FILTER_SETTINGS, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

# Load settings on start
load_settings()

def match_ignore(name, is_dir=False):
    # 1. Check Exceptions (Always Show)
    if name in FILTER_SETTINGS["temp_visible"]:
        return False
        
    # 2. Check Global Hidden Toggle
    if FILTER_SETTINGS["show_hidden"]:
        if name in {".git", ".idea", ".vscode"}: # Keep extreme core files hidden 
            return True
        return False

    # 3. Check Custom Rules
    if name in FILTER_SETTINGS["rules_exact"]: 
        return True
    
    for prefix in FILTER_SETTINGS["rules_startswith"]:
        if prefix and name.startswith(prefix): return True
        
    for suffix in FILTER_SETTINGS["rules_endswith"]:
        if suffix and name.endswith(suffix): return True
        
    for substring in FILTER_SETTINGS["rules_contains"]:
        if substring and substring in name: return True

    # 4. Check Default Hardcoded Rules (from constants.py)
    if name.startswith("."): 
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