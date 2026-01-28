import sys
import os
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    default_path = "/home/lazydev/flutter/twb_roleplay"
    
    if not os.path.exists(default_path):
        default_path = os.getcwd()

    window = MainWindow(default_path)
    window.show()
    sys.exit(app.exec())