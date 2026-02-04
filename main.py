import sys
import os
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Optional: Increase font size slightly for high DPI
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)
    
    default_path = "/home/ck_the_dev/Documents/apps/"
    
    if not os.path.exists(default_path):
        default_path = os.getcwd()

    window = MainWindow(default_path)
    window.showMaximized() # Start maximized to use all space
    sys.exit(app.exec())