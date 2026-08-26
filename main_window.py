import os
from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout
from project_panel import ProjectPanel

class MainWindow(QMainWindow):
    def __init__(self, default_folder):
        super().__init__()
        self.setWindowTitle("Vibe Workspace")
        self.resize(1400, 900)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.grid_layout = QGridLayout(self.central_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(1) 
        
        self.project_panels = []
        self.add_project_space(default_folder)

    def add_project_space(self, folder=None):
        if len(self.project_panels) >= 4:
            return

        panel = ProjectPanel(folder)
        panel.close_requested.connect(self.remove_project_space)
        panel.add_requested.connect(lambda: self.add_project_space())
        
        self.project_panels.append(panel)
        self.rearrange_grid()

    def remove_project_space(self, panel_to_remove):
        if len(self.project_panels) > 1:
            self.grid_layout.removeWidget(panel_to_remove)
            panel_to_remove.setParent(None)
            self.project_panels.remove(panel_to_remove)
            panel_to_remove.deleteLater()
            self.rearrange_grid()

    def rearrange_grid(self):
        # Detach all current widgets from the grid
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        count = len(self.project_panels)
        
        # Reset stretches so they apply correctly to the new setup
        self.grid_layout.setRowStretch(0, 0)
        self.grid_layout.setRowStretch(1, 0)
        self.grid_layout.setColumnStretch(0, 0)
        self.grid_layout.setColumnStretch(1, 0)

        if count == 1:
            self.grid_layout.addWidget(self.project_panels[0], 0, 0)
            self.grid_layout.setRowStretch(0, 1)
            self.grid_layout.setColumnStretch(0, 1)

        elif count == 2:
            self.grid_layout.addWidget(self.project_panels[0], 0, 0)
            self.grid_layout.addWidget(self.project_panels[1], 0, 1)
            self.grid_layout.setRowStretch(0, 1)
            self.grid_layout.setColumnStretch(0, 1) # Left half
            self.grid_layout.setColumnStretch(1, 1) # Right half

        elif count == 3:
            self.grid_layout.addWidget(self.project_panels[0], 0, 0, 2, 1)
            self.grid_layout.addWidget(self.project_panels[1], 0, 1)
            self.grid_layout.addWidget(self.project_panels[2], 1, 1)
            self.grid_layout.setRowStretch(0, 1)
            self.grid_layout.setRowStretch(1, 1)
            self.grid_layout.setColumnStretch(0, 1)
            self.grid_layout.setColumnStretch(1, 1)

        elif count == 4:
            self.grid_layout.addWidget(self.project_panels[0], 0, 0)
            self.grid_layout.addWidget(self.project_panels[1], 0, 1)
            self.grid_layout.addWidget(self.project_panels[2], 1, 0)
            self.grid_layout.addWidget(self.project_panels[3], 1, 1)
            self.grid_layout.setRowStretch(0, 1)
            self.grid_layout.setRowStretch(1, 1)
            self.grid_layout.setColumnStretch(0, 1)
            self.grid_layout.setColumnStretch(1, 1)